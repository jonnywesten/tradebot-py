import backtrader as bt
from strategies.Base import BaseForOptimzeStrategy
from strategies.Base import BaseStrategy


class MaCrossMultiple(BaseForOptimzeStrategy):
    params = (
        ('fast', 15),
        ('slow', 30)
    )

    def __init__(self):
        self.crossovers = []

        for d in self.datas:
            ma_fast = bt.ind.SMA(d, period=self.params.fast)
            ma_slow = bt.ind.SMA(d, period=self.params.slow)

            self.crossovers.append(bt.ind.CrossOver(ma_fast, ma_slow))

    def next(self):
        for i, d in enumerate(self.datas):
            if not self.getposition(d).size:
                if self.crossovers[i] > 0:
                    self.buy(data=d)
            elif self.crossovers[i] < 0:
                self.close(data=d)
