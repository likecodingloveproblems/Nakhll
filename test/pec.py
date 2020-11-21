from zeep import Client

saleService = Client('https://pec.shaparak.ir/NewIPGServices/Sale/SaleService.asmx?wsdl')
ClientSaleRequestData = saleService.get_type('ns0:ClientSaleRequestData')
PIN = 'Qu88TflPdWiv5f3nPk8g'
data = ClientSaleRequestData(LoginAccount=PIN, Amount=1000, OrderId=3, CallBackUrl='', AdditionalData='only simple test', Originator='just a test')
print(data)
res = saleService.service.SalePaymentRequest(data)
print(res)
