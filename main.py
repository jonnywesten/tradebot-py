import numpy as np
import datetime as dt  # For datetime objects

import pandas
import pandas_datareader.data as web
from dateutil.relativedelta import relativedelta
import matplotlib
import backtrader as bt
import pandas as pd
import os

from analyzers.tradeAnalyzer import printTradeAnalysis

matplotlib.use('TkAgg')
from strategies.BuyAndHoldMultiple import BuyAndHoldMultiple
from strategies.Axel import AxelStrategy
from strategies.BuyAndHold import BuyAndHold
from strategies.MaCrossMultiple import MaCrossMultiple
from strategies.TrendFollowing import ClenowTrendFollowingStrategy
from strategies.Momentum import MomentumStrategy
from strategies.RSICCI import RSICCI


def runStrategy500(strategy):
    cerebro = bt.Cerebro()
    cerebro.broker.set_coc(True)

    cerebro.addstrategy(strategy)

    folderName = 'data/' + dt.datetime.today().strftime('%Y-%m-%d')

    stocks = os.listdir(folderName)[:5]

    for filename in stocks:
        f = os.path.join(folderName, filename)
        df = pandas.read_csv(f, parse_dates=True, delimiter=",")
        df['Date'] = pd.to_datetime(df['Date'])
        df.set_index('Date', inplace=True)
        data = bt.feeds.PandasData(dataname=df, plot=True)
        cerebro.adddata(data, name=filename)

    INITIAL_CASH = 10000
    cerebro.broker.setcash(INITIAL_CASH)
    cerebro.addsizer(bt.sizers.PercentSizer, percents=100 / len(stocks))
    cerebro.broker.setcommission(commission=0.001)

    cerebro.addobserver(bt.observers.Value)
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, timeframe=bt.TimeFrame.Days, compression=1, factor=365,
                        annualize=True)
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="ta")
    cerebro.addanalyzer(bt.analyzers.DrawDown)
    cerebro.addanalyzer(bt.analyzers.Returns, timeframe=bt.TimeFrame.Days, compression=1, tann=365)
    cerebro.addanalyzer(bt.analyzers.TimeReturn, timeframe=bt.TimeFrame.NoTimeFrame)
    # cerebro.addanalyzer(bt.analyzers.TimeReturn, timeframe=bt.TimeFrame.NoTimeFrame, data=data, _name='buyandhold')

    results = cerebro.run(maxcpus=8)
    assert len(results) == 1

    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    print(f'Number of trades: {results[0].analyzers.ta.get_analysis().total.total}')
    print('PnL: %.2f' % (cerebro.broker.getvalue() - INITIAL_CASH,))
    print('Sharpe Ratio: ', results[0].analyzers.sharperatio.get_analysis()['sharperatio'])
    print('CAGR: %.2f%%' % (results[0].analyzers.returns.get_analysis()['ravg'] * 100,))
    print('Total return: %.2f%%' % (list(results[0].analyzers.timereturn.get_analysis().values())[0] * 100,))
    print('Max Drawdown: %.2f%%' % results[0].analyzers.drawdown.get_analysis().max.drawdown)
    # print('Buy and Hold: {0:.2f}%'.format(list(results[0].analyzers.buyandhold.get_analysis().values())[0] * 100))

    cerebro.plot()

    return cerebro


def runStrategySingle(strategy, plot=True):
    cerebro = bt.Cerebro()
    cerebro.addstrategy(strategy)

    start = dt.datetime.now() - relativedelta(years=2)
    end = dt.datetime.now() - relativedelta(years=0)

    df = web.DataReader('KO', "yahoo", start, end)
    print(df.head())
    data = bt.feeds.PandasData(dataname=df, plot=True)
    cerebro.adddata(data)

    cerebro.broker.setcash(100000)
    cerebro.addsizer(bt.sizers.AllInSizerInt, percents=90)
    cerebro.broker.setcommission(commission=0.001)

    cerebro.run(sdtstats=False)
    if plot:
        cerebro.plot(style='candlestick')

    return cerebro


if __name__ == '__main__':
    runStrategy500(AxelStrategy)
    # runStrategy500(BuyAndHoldMultiple)
