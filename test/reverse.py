from zeep import Client
reverseService = Client('https://pec.shaparak.ir/NewIPGServices/Reverse/ReversalService.asmx?wsdl')
ClientReversalRequestData = reverseService.get_type('ns0:ClientReversalRequestData')
PIN = 'Qu88TflPdWiv5f3nPk8g'
data = ClientReversalRequestData(LoginAccount=PIN, Token='98460301692803')
print(data)
res = reverseService.service.ReversalRequest(data)
print(res)
