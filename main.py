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
from strategies.TrendFollowing import ClenowTrendFollowingStrategy


def runStrategy(strategy):
    cerebro = bt.Cerebro()
    cerebro.addstrategy(strategy)

    start = dt.datetime.now() - relativedelta(years=2)
    end = dt.datetime.now() - relativedelta(years=0)

    stocks = ['AMZN']
    data = 0
    for s in stocks:
        df = web.DataReader(s, "yahoo", start, end)
        data = bt.feeds.PandasData(dataname=df)
        cerebro.adddata(data, name=s)

    INITIAL_CASH = 10000
    cerebro.broker.setcash(INITIAL_CASH)
    cerebro.addsizer(bt.sizers.FixedSize, stake=1)
    cerebro.broker.setcommission(commission=0.001)

    cerebro.addanalyzer(bt.analyzers.SharpeRatio, timeframe=bt.TimeFrame.Days, compression=1, factor=365,
                        annualize=True)
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="ta")
    cerebro.addanalyzer(bt.analyzers.DrawDown)
    cerebro.addanalyzer(bt.analyzers.Returns, timeframe=bt.TimeFrame.Days, compression=1, tann=365)
    cerebro.addanalyzer(bt.analyzers.TimeReturn, timeframe=bt.TimeFrame.NoTimeFrame)
    cerebro.addanalyzer(bt.analyzers.TimeReturn, timeframe=bt.TimeFrame.NoTimeFrame, data=data, _name='buyandhold')

    results = cerebro.run()
    assert len(results) == 1

    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    print(f'Number of trades: {results[0].analyzers.ta.get_analysis().total.total}')
    print('PnL: %.2f' % (cerebro.broker.getvalue() - INITIAL_CASH,))
    print('Sharpe Ratio: ', results[0].analyzers.sharperatio.get_analysis()['sharperatio'])
    print('CAGR: %.2f%%' % (results[0].analyzers.returns.get_analysis()['ravg'] * 100,))
    print('Total return: %.2f%%' % (list(results[0].analyzers.timereturn.get_analysis().values())[0] * 100,))
    print('Max Drawdown: %.2f%%' % results[0].analyzers.drawdown.get_analysis().max.drawdown)
    print('Buy and Hold: {0:.2f}%'.format(list(results[0].analyzers.buyandhold.get_analysis().values())[0] * 100))

    cerebro.plot()

    return cerebro


if __name__ == '__main__':
    runStrategy(ClenowTrendFollowingStrategy)
    # runStrategy(BuyAndHoldMultiple)
