import os
import binascii
from issuer.blockchain_service import BlockchainService
from mainsite import TOP_DIR
from django.test import TestCase
import time


class TestBlockchainService(TestCase):

    @classmethod
    def setUpClass(cls):
        super(TestBlockchainService, cls).setUpClass()
        factomd_host = 'http://localhost:8088'
        factom_walletd_host = 'http://localhost:8089'
        ec_address = 'EC2yPMoPTKNW53TKNzwqG9pfcAKW9BDchZPWuJbnGFF4gLBJ2aAu'
        secret_signing_seed = 'fc67c820e0fe764dc9d3536ae753de67cd29ca07a7774849f7e238a471dfcd8a'
        cls.blockchain_service = BlockchainService(factomd_host,
                                                    factom_walletd_host,
                                                    ec_address,
                                                    secret_signing_seed)

    def test_blockchain_write(self):
        resp = self.blockchain_service.write(['test', 'external', 'ids'], 'test-content')
        assert resp['message'] == 'Entry Reveal Success'

    def test_hash(self):
        hash_string = binascii.hexlify(self.blockchain_service.input_to_hash_bytes(bytes('test_hash')))
        assert hash_string == '6b70a820eb978882fa49b199c853a5676e5e1a4744371be5affd4b3af1f5dde6'

    def test_image_hash(self):
        image_path = self.get_test_image_path()
        with open(image_path) as f:
            img_bytes = bytes(f.read())
            img_hash = binascii.hexlify(self.blockchain_service.input_to_hash_bytes(img_bytes))
            assert img_hash == 'b13ef6e8ac7d409e6d7990e47470fd4eb005fcd0a3cdc178257550758365ffa0'

    def test_signature(self):
        msg = bytes('test-signature')
        sig = self.blockchain_service.create_signature(msg)
        assert msg == self.blockchain_service.signature_to_msg(sig, self.blockchain_service.public_key)

    def test_register(self):
        image_path = self.get_test_image_path()
        with open(image_path) as f:
            img_bytes = bytes(f.read())
            resp = self.blockchain_service.register(img_bytes)
            time.sleep(10)
            assert resp['message'] == 'Entry Reveal Success'

    def test_verify(self):
        image_path = self.get_test_image_path()
        with open(image_path) as f:
            img_bytes = bytes(f.read())
            verify_msg = self.blockchain_service.verify(img_bytes, '903087db475049f5d2203bfdf9709bcc626ff52d7aa9bd46dea5f6a6540a1e56')
            assert verify_msg['verified']

    @staticmethod
    def get_testfiles_path(*args):
        return os.path.join(TOP_DIR, 'apps', 'issuer', 'testfiles', *args)

    def get_test_image_path(self):
        return os.path.join(self.get_testfiles_path(), 'guinea_pig_testing_badge.png')
