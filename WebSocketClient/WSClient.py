import gdax

# how many future trades we are tracking, for trends
MAX_RECORDS = 5
PROFIT_MARGIN = 100.0

class State(object):
    INITIATE_BUY = 0
    BUY_POINT_REACHED = 1
    INITIATE_SELL = 2
    SELL_POINT_REACHED = 3

class WSClient(gdax.WebsocketClient):
    def on_open(self):
        self.url = "wss://ws-feed.gdax.com/"
        self.products = ["BTC-USD"]
        self.message_count = 0
        self.balance = 5000.0
        self.buy_point = 4250.0
        self.sell_point = None
        self.buying = True
        self.transactions = 0
        self.show_transaction = False
        self.state = State.INITIATE_BUY
        self.trade_records = []
        print("buying {0}, entry point ${1}".format(self.buying, self.buy_point))

    def on_message(self, msg):
        self.message_count += 1
        if 'price' in msg and 'type' in msg:
            order_type = msg['type']
            if order_type == 'done':
                reason = msg['reason']
                if reason == 'filled':
                    price = float(msg["price"])
                    side = msg['side']
                    if self.buying:
                        if side == 'buy':
                            self.process_buy(price)
                    else:
                        if side == 'sell':
                            self.process_sell(price)

            if self.show_transaction:
                print("New transaction: current balance: ${0}".format(self.balance))
                self.show_transaction = False
            #print ("Message type: {0}\t{1}\treason: {2}".format(msg["type"], float(msg["price"]), msg["reason"]))

    # if we are buying, the price has dropped to our pre-set buy point
    # keep monitoring to see if the price will continue to drop
    def process_buy(self, current_price):
        if self.state == State.INITIATE_BUY:
            if current_price <= self.buy_point:
                self.buy_point_reached()
        elif self.state == State.BUY_POINT_REACHED:
            self.handle_buy_point_reached(current_price)

    def buy_point_reached(self):
        self.state = State.BUY_POINT_REACHED
        self.trade_records = []

    # in this state, we monitor a set of future transactions, if future prices are
    # trending downward, reset the buy point
    # TODO: when monitoring future transactions, give more weight to trade with large size
    def handle_buy_point_reached(self, current_price):
        count = len(self.trade_records)
        if count < MAX_RECORDS:
            self.trade_records.append(current_price)
        else:
            average_price = (reduce(lambda x, y: x + y, self.trade_records)) / float(MAX_RECORDS)
            print("average price when buy point reached: ${0}".format(average_price))
            # trending downward, lower the buy point and keep monitoring
            if average_price < self.buy_point:
                self.buy_point = average_price
                self.trade_records = []
            else:
                # we have a up tick or no change, buy now
                self.buy_coin(current_price)

    # Need to fine tune the buy price to make sure the price we set is lower than the current market price
    # to avoid paying the taker fee
    def buy_coin(self, current_price):
        self.balance -= current_price
        self.buying = False
        self.state = State.INITIATE_SELL
        self.sell_point = current_price + PROFIT_MARGIN
        self.transactions += 1
        self.show_transaction = True
        print("Buying at ${0}".format(current_price))

    def process_sell(self, current_price):
        if self.state == State.INITIATE_SELL:
            if current_price >= self.sell_point:
                self.sell_point_reached()
        elif self.state == State.SELL_POINT_REACHED:
            self.handle_sell_point_reached(current_price)

    def sell_point_reached(self, price):
        self.state = State.SELL_POINT_REACHED
        self.trade_records = []

    def handle_sell_point_reached(self, current_price):
        count = len(self.trade_records)
        if count < MAX_RECORDS:
            self.trade_records.append(current_price)
        else:
            average_price = (reduce(lambda x, y: x + y, self.trade_records)) / float(MAX_RECORDS)
            print("average price when sell point reached: ${0}".format(average_price))
            # trending upward, keep monitoring the price
            if average_price > self.sell_point:
                self.sell_point = average_price
                self.trade_records = []
            else:
                # we have a down tick or no change, sell now
                self.sell_coin(current_price)

    # Need to fine tune the sell price to make sure the price we set is higher than the current market price
    # to avoid paying the taker fee
    def sell_coin(self, current_price):
        self.balance += current_price
        self.buying = True
        self.transactions += 1
        self.buy_point = current_price - PROFIT_MARGIN
        self.show_transaction = True
        print("Selling at ${0}".format(current_price))

    def on_close(self):
        print("-- Goodbye! --")
