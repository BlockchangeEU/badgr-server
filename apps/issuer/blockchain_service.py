from factom import FactomWalletd
from django.conf import settings
from issuer.blockchain_utils import BlockchainRegistrationError
import nacl.hash
import nacl.encoding
import nacl.signing
import nacl.exceptions
import uuid
import time
import binascii

from issuer.factom_api_service import ExtendedFactomd


class BlockchainService:

    """
    Initializes a connection with factomd and factom-walletd
    as well as instantiates a private key for signing

    :param factomd_host: Address where factomd is listening. ex. "http://localhost:8080"
    :type factomd_host: str
    :param factom_walletd_host: Address where factom-walletd is listening
    :type factom_walletd_host: str
    :param ec_address: EC address used to fund entries
    :type ec_address: str
    :param secret_seed: Secret seed for private key in hex
    :type secret_seed: str (hex)
    """
    def __init__(self, factomd_host, factom_walletd_host, ec_address, secret_seed, chain_id=None):
        self.factomd = ExtendedFactomd(
            host=factomd_host,
            ec_address=ec_address
        )

        self.walletd = FactomWalletd(
            host=factom_walletd_host,
            ec_address=ec_address
        )

        if chain_id is None:
            chain_create_response = self.initialize_new_chain()
            self.chain_id = chain_create_response['chainid']
        else:
            self.chain_id = chain_id

        self.private_key = nacl.signing.SigningKey(binascii.unhexlify(secret_seed))
        self.public_key = self.private_key.verify_key

    def write(self, ext_ids, content):
        commit_response = self.walletd.new_entry(self.factomd, self.chain_id, ext_ids, content)

        if commit_response['message'] != 'Entry Reveal Success':
            raise BlockchainRegistrationError(commit_response.message)

        entryhash = commit_response['entryhash']

        ack_resp = self.factomd.ack(entryhash, self.chain_id)
        while (ack_resp['entrydata']['status'] != 'DBlockConfirmed'
               and ack_resp['entrydata']['status'] != 'TransactionACK'):
            time.sleep(2)
            ack_resp = self.factomd.ack(entryhash, self.chain_id)

        return commit_response

    def create_signature(self, input_data):
        return self.private_key.sign(input_data, encoder=nacl.encoding.RawEncoder)

    def initialize_new_chain(self):
        badgr_app_id = getattr(settings, 'BADGR_APP_ID')
        chain_create_response = self.walletd.new_chain(
            self.factomd,
            ['badgr-server', str(badgr_app_id), 'UUID: ' + str(uuid.uuid1())],
            'Badge Commitment Chain'
        )

        time.sleep(2)

        if chain_create_response['message'] != 'Entry Reveal Success':
            raise BlockchainRegistrationError(chain_create_response['message'])

        return chain_create_response

    def verify_signed_entry(self, chain_entry, public_key_seed):
        timestamp_bytes = binascii.unhexlify(chain_entry['extids'][0])
        public_key = nacl.signing.VerifyKey(binascii.unhexlify(public_key_seed))
        hash_signature_string = chain_entry['extids'][2]
        content = chain_entry['content']

        hash_bytes = binascii.unhexlify(content)
        msg = timestamp_bytes.join(hash_bytes)
        signed_msg = binascii.unhexlify(hash_signature_string)

        try:
            msg_result = self.signature_to_msg(signed_msg, public_key)
        except nacl.exceptions.BadSignatureError:
            return False

        return msg == msg_result

    def register(self, input_data):

        timestamp_bytes = bytes(int(time.time()))
        hash_bytes = self.input_to_hash_bytes(input_data)
        hash_signature_bytes = self.create_signature(timestamp_bytes.join(hash_bytes))

        content = binascii.hexlify(hash_bytes)
        ext_ids = [binascii.hexlify(timestamp_bytes),
                   binascii.hexlify(bytes(self.public_key)),
                   binascii.hexlify(hash_signature_bytes)]

        commit_response = self.write(ext_ids, content)
        if commit_response['message'] != 'Entry Reveal Success':
            raise BlockchainRegistrationError(commit_response['message'])

        return commit_response

    def verify(self, input_data, public_key_seed):

        hash_string = binascii.hexlify(self.input_to_hash_bytes(input_data))
        chain_data = self.factomd.read_chain(self.chain_id)

        entries = [chain_entry for chain_entry in chain_data
                   if chain_entry['content'] == hash_string
                   and chain_entry['extids'][1] == public_key_seed]

        if len(entries) < 1:
            return {'message': 'Entry not found in chain {}'.format(self.chain_id), 'verified':False}

        for chain_entry in entries:
            if self.verify_signed_entry(chain_entry, public_key_seed):
                return {'message': 'Entry found in chain {}'.format(self.chain_id), 'verified':True}

        return {'message': ' Entry found in chain {} but signature was invalid'.format(self.chain_id), 'verified': False}

    @staticmethod
    def input_to_hash_bytes(input_data):
        return nacl.hash.sha256(input_data, encoder=nacl.encoding.RawEncoder)

    @staticmethod
    def signature_to_msg(signed_msg, public_key):
        return public_key.verify(signed_msg, encoder=nacl.encoding.RawEncoder)
