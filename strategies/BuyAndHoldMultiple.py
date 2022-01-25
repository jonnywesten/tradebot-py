from strategies.Base import BaseStrategy
import math
from pprint import pprint


class BuyAndHoldMultiple(BaseStrategy):
    def next(self):
        for i, d in enumerate(self.datas):
            if d[0] > 0.0 and not self.getposition(d).size:
                size = math.floor(int(self.broker.get_cash() / len(self.datas)) / (d[0] * 1.02))
                self.buy(data=d, size=size)

    def prenext(self):
        for i, d in enumerate(self.datas):
            # if data is there
            if d.lines[0]._idx > -1 and not self.getposition(d).size:
                size = math.floor(int(self.broker.get_cash() / len(self.datas)) / (d[0] * 1.02))
                self.buy(data=d, size=size)
