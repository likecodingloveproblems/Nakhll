
class SkipItemException(Exception):
    '''
    Exception to be raised when an item should be skipped.
    '''
    def __init__(self, message=None, *args):
        self.message = message
