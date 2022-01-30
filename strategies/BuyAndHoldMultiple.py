from strategies.Base import BaseStrategy
import math


class BuyAndHoldMultiple(BaseStrategy):
    def next(self):
        for i, d in enumerate(self.datas):
            if d.lines[0]._idx > -1 and not self.getposition(d).size:
                self.buy(data=d)

    def prenext(self):
        # call next() even when data is not available for all tickers
        self.next()
