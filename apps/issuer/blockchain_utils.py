

class BlockchainRegistrationError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr('Could not register on the blockchain. Commit failed with message:' + self.message)

