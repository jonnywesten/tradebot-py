from strategies.Base import BaseStrategy


class BuyAndHold(BaseStrategy):
    def nextstart(self):
        # Buy all the available cash
        size = int(self.broker.get_cash() / self.data)
        self.buy(size=size)
