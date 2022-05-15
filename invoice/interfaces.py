
class AccountingInterface:
    def payment_result(self, payment_id):
        ''' Get payment object, and proceed shoping ... 
        
            if the invoice related to payment has coupon, the coupon
            should applied.
        '''