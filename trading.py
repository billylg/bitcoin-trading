import time
from WebSocketClient.WSClient import WSClient
import gdax


# auth_client = gdax.AuthenticatedClient('9bb3f67c0a3b0da08ca0e30ea26bfa44',
#         'A/0gf1p6M7yYW6M5QVBYe6lx9S1Ahicc6oIz3FqsbnS6ZX2ozo6vaGjiHjHR6A5rK8yOpTIet+RMmHzT0Ka1+w==',
#         'cpaf0whl3k')
# accounts = auth_client.get_accounts()
# account_id = '2593e508-c366-49ca-9999-c0aa7f57ea42'
# auth_client.buy(size='1.0', product_id='BTC-USD')
# auth_client.buy(price='4000.00', #USD
#                size='1.00', #BTC
#                product_id='BTC-USD')
# print accounts

wsClient = WSClient()
wsClient.start()
print(wsClient.url, wsClient.products)
while (True):
    #print ("\nmessage_count = {0}\n".format(wsClient.message_count))
    time.sleep(1)
wsClient.close()
