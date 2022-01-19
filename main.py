from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import numpy as np
import datetime as dt  # For datetime objects
import pandas_datareader.data as web
from dateutil.relativedelta import relativedelta
import matplotlib
import backtrader as bt

from analyzers.tradeAnalyzer import printTradeAnalysis

matplotlib.use('TkAgg')
from strategies.BuyAndHoldMultiple import BuyAndHoldMultiple
from strategies.MaCrossMultiple import MaCrossMultiple


def runStrategy(strategy):
    cerebro = bt.Cerebro()
    cerebro.addstrategy(strategy)

    start = dt.datetime.now() - relativedelta(years=4)
    end = dt.datetime.now() - relativedelta(years=3)

    stocks = ['AAPL', 'MSFT', 'AMZN', 'TSLA', 'GOOG']

    for s in stocks:
        df = web.DataReader(s, "yahoo", start, end)
        data = bt.feeds.PandasData(dataname=df)
        cerebro.adddata(data, name=s)

    cerebro.broker.setcash(100000.0)
    cerebro.addsizer(bt.sizers.FixedSize, stake=1)
    cerebro.broker.setcommission(commission=0.001)

    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="ta")
    back = cerebro.run()
    printTradeAnalysis(back[0].analyzers.ta.get_analysis())

    cerebro.plot()

    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    return back


if __name__ == '__main__':
    runStrategy(MaCrossMultiple)
    # runStrategy(BuyAndHoldMultiple)
