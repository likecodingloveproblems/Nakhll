from abc import ABC, abstractmethod


SUCCESS_STATUS = 'success'
FAILURE_STATUS = 'failure'


class PaymentMethodAbstract(ABC):
    """Abstract class for payment methods

    Every payment method should implement the following methods:
        - initiate_payment()
        - payment_callback()
    """

    def __init__(self, *args, **kwargs):
        self.transaction = None

    @abstractmethod
    def initiate_payment(self, data):
        """Generate ipg url and redirect user to that url

        Args:
            data (dict): Data for payment

        Returns:
            Response: Response with redirect url like:
                :py:`{'url': 'https://ipg.com/payment/'}`
        """

    @abstractmethod
    def callback(self, data):
        """Handle returned data from IPG

        Validate IPG response and update transaction result, connect data
        to transaction object

        Args:
            data (dict): Raw Data from IPG, that should be parsed based on each payment method

        Returns:
            dict: Response with status and message like:
                :py:`return {'status': self.FAILURE_STATUS, 'code': transaction_result.order_id}`
                note: in case of failure, transaction_result.order_id will be used as code,
                but in case of success, referrer_object.id will be used as code
        """
