
class PrintFailureError(Exception):

    # do no collect as a pytest
    __test__ = False

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

