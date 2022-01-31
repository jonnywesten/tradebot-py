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
        orderList = []
        for d in self.params.datas:
            try:
                orderList.append([d._name, self.params.inds[d]["dtm"][self.i]])
            except IndexError:
                pass

        def takeSecond(elem):
            return elem[1]

        orderList.sort(key=takeSecond)
        self.l.pos[0] = [item[0] for item in orderList].index(self.data._name)


class AxelStrategy(BaseStrategy):
    params = (
        ('maperiod', 50),
        ('days', 15)
    )

    def __init__(self):
        self.inds = dict()
        for d in self.datas:
            self.inds[d] = dict()
            self.inds[d]["sma"] = bt.indicators.SimpleMovingAverage(d.close, period=self.params.maperiod)
            self.inds[d]["dtm"] = DistanceToMA(d)

        for d in self.datas:
            self.inds[d]["pos"] = RankingPosition(d, days=self.params.days, datas=self.datas, inds=self.inds)

    def next(self):
        for d in self.datas:
            if d.lines[0]._idx > -1 and not self.getposition(d).size and \
                    self.inds[d]["pos"][0] > self.inds[d]["pos"][-1] and \
                    self.inds[d]["pos"][0] > len(self.datas) / 4 - math.floor(len(self.datas) / 4):
                self.buy(data=d)
                self.sell(data=d, exectype=bt.Order.StopTrail,
                          trailpercent=0.2)  # last price will be used as reference

    def prenext(self):
        # call next() even when data is not available for all tickers
        self.next()
