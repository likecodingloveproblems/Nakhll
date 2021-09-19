class NoTransactionException(Exception):
    """
    Exception raised when a transaction is not found.
    """

class NoCompletePaymentMethodException(Exception):
    """
    Exception raised when complete_payment method for given model is not found.
    """