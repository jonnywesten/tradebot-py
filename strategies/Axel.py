from strategies.Base import BaseStrategy
import backtrader as bt
import math
from pprint import pprint


class DistanceToMA(bt.Indicator):
    lines = ('dtm',)
    params = dict(maperiod=50)

    def __init__(self):
        sma = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.maperiod)
        self.l.dtm = 100 / (self.data.close / (self.data.close - sma))


class RankingPosition(bt.indicators.PeriodN):
    lines = ('pos',)
    params = dict(days=5, datas=dict(), inds=dict())

    def __init__(self):
        self.i = 0

    def next(self):
        if self.i % self.params.days == 0:
            self.calculate_position()
        else:
            self.lines.pos[0] = self.lines.pos[-1]
        self.i += 1

    def calculate_position(self):
        self.lines.pos[0] = 4

        print(self.i)
        # only look at data that we can have indicators for
        for i, d in enumerate(self.params.datas):
            try:
                print(self.params.inds[d]["dtm"][i])
            except IndexError:
                print("error for index " + str(i))

        self.rankings = list(filter(lambda d: len(d) > 1, self.params.datas))
        self.rankings.sort(key=lambda d: self.params.inds[d]["dtm"][0])
        for i, d in enumerate(self.rankings):
            print(d._name)


class AxelStrategy(BaseStrategy):
    params = (
        ('maperiod', 50),
        ('days', 30)
    )

    def __init__(self):
        self.inds = dict()
        for i, d in enumerate(self.datas):
            self.inds[d] = dict()
            self.inds[d]["sma"] = bt.indicators.SimpleMovingAverage(d.close, period=self.params.maperiod)
            self.inds[d]["dtm"] = DistanceToMA(d)

        for i, d in enumerate(self.datas):
            self.inds[d]["pos"] = RankingPosition(d, days=self.params.days, datas=self.datas, inds=self.inds)

    def next(self):
        pass

    def prenext(self):
        # call next() even when data is not available for all tickers
        self.next()
