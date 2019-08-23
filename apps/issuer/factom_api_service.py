from factom import Factomd

class ExtendedFactomd(Factomd):

    def ack(self, hash, chainid, fulltransaction=''):
        return self._request('ack', params={
            'hash': hash,
            'chainid': chainid,
            'fulltransaction': fulltransaction
        })

