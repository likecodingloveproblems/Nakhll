class NoTransactionException(Exception):
    """
    Exception raised when a transaction is not found.
    """

class NoCompletePaymentMethodException(Exception):
    """
    Exception raised when complete_payment method for given model is not found.
    """

class NoAddressException(Exception):
    """
    Exception raised when no address is set for invoice.
    """

class OutOfPostRangeProductsException(Exception):
    """
    Exception raised when one or more products cannot be sent to user address
    """

class InvoiceExpiredException(Exception):
    """
    Exception raised when invoice is expired.
    """

class InvalidInvoiceStatusException(Exception):
    """
    Exception raised when invoice status is invalid.
    """