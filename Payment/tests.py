from zeep import Client

PIN = 'Qu88TflPdWiv5f3nPk8g'
### simulate successful payment ###
# sale service initialization
saleService = Client('https://pec.shaparak.ir/NewIPGServices/Sale/SaleService.asmx?wsdl')
saleRequestData = saleService.get_type('ns0:ClientSaleRequestData')
# confirm service initialization
confirmService = Client('https://pec.shaparak.ir/NewIPGServices/Confirm/ConfirmService.asmx?WSDL')
confirmRequestData = confirmService.get_type('ns0:ClientConfirmRequestData')
# reverse service initialization
reverseService = Client('https://pec.shaparak.ir/NewIPGServices/Reverse/ReversalService.asmx?WSDL')
reverseRequestData = reverseService.get_type('ns0:ClientReversalRequestData')

def test_sale_request():
    data = saleRequestData(LoginAccount='Qu88TflPdWiv5f3nPk8g', 
                        Amount='10000', OrderId='2',
                        CallBackUrl='https://nakhll.com/cart/verify/', 
                        AdditionalData = 'this is a test ...', 
                        Originator='a test on PAC by developer...')
    response = saleService.service.SalePaymentRequest(data)
    print(response)

    url = 'https://pec.shaparak.ir/NewIPG/?token={}'.format(response['Token'])
    print('Url: {}'.format(url))

def test_confirm_sale():
    token = 96853760656344
    data = confirmRequestData(LoginAccount=PIN, Token=token)
    response = confirmService.service.ConfirmPayment(data)
    if response['Status'] == -1531:
        print('‫باشد‬ ‫ی‬ ‫نم‬ ‫ر‬ ‫ی‬ ‫پذ‬ ‫امکان‬ ‫ناموفق‬ ‫تراکنش‬ ‫د‬ ‫یی‬ ‫تا‬')
    elif response['Status'] == -1532:
        print('‫شد‬ ‫د‬ ‫یی‬ ‫تا‬ ‫رنده‬ ‫ی‬ ‫پذ‬ ‫ی‬ ‫سو‬ ‫از‬ ‫تراکنش‬')
    elif response['Status'] == -1533:
        print('‫است‬ ‫شده‬ ‫د‬ ‫یی‬ ‫تا‬ ‫قبالً‬ ‫تراکنش‬')
    elif response['Status'] == -1540:
        print('‫باشد‬ ‫می‬ ‫ناموفق‬ ‫تراکنش‬ ‫تایید‬')
    elif response['Status'] == -1545:
        print('‫بود‬ ‫ناموفق‬ ‫ه‬ ‫ی‬ ‫د‬ ‫یی‬ ‫تا‬ ‫تراکنش‬ ‫ارسال‬ ‫از‬ ‫ش‬ ‫ی‬ ‫پ‬ ‫تراکنش‬ ‫ت‬ ‫ی‬ ‫وضع‬ ‫درج‬')
    print(response)

print('start tests ...')
# test_sale_request()
test_confirm_sale()
print('end tests ...')
