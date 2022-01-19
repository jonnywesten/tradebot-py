from strategies.Base import BaseStrategy
import math


class BuyAndHoldMultiple(BaseStrategy):
    def nextstart(self):
        for i, d in enumerate(self.datas):
            size = math.floor(int(self.broker.get_cash() / len(self.datas)) / (d[0] * 1.02))
            self.buy(data=d, size=size)
