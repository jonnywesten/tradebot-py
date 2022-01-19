import backtrader as bt
from strategies.Base import BaseStrategy
from pprint import pprint


class DonchianChannelsIndicator(bt.Indicator):
    '''Donchian channel.'''

    alias = ('DCH', 'DonchianChannel',)

    lines = ('dcm', 'dch', 'dcl',)  # dc middle, dc high, dc low

    params = (
        ('period', 20),  # lookback period
    )

    plotinfo = dict(subplot=False)  # plot along with data
    plotlines = dict(
        dcm=dict(ls='--'),  # dashed line
        dch=dict(_samecolor=True),  # use same color as prev line (dcm)
        dcl=dict(_samecolor=True),  # use same color as prev line (dch)
    )

    def __init__(self):
        super().__init__()
        self.addminperiod(self.params.period + 1)
        self.lines.dch = bt.indicators.Highest(self.data.high(-1), period=self.params.period)
        self.lines.dcl = bt.indicators.Lowest(self.data.low(-1), period=self.params.period)
        self.lines.dcm = (self.lines.dch + self.lines.dcl) / 2.0  # avg of the above


class ClenowTrendFollowingStrategy(BaseStrategy):
    """The trend following strategy from the book "Following the trend" by Andreas Clenow."""
    alias = ('MeanReversion',)

    params = (
        ('trend_filter_fast_period', 50),
        ('trend_filter_slow_period', 100),
        ('fast_donchian_channel_period', 25),
        ('slow_donchian_channel_period', 50),
        ('trailing_stop_atr_period', 100),
        ('trailing_stop_atr_count', 3),
        ('risk_factor', 0.002)
    )

    def __init__(self):
        self.trend_filter_fast = bt.indicators.EMA(period=self.params.trend_filter_fast_period)
        self.trend_filter_slow = bt.indicators.EMA(period=self.params.trend_filter_slow_period)
        self.dc_fast = DonchianChannelsIndicator(period=self.params.fast_donchian_channel_period)
        self.dc_slow = DonchianChannelsIndicator(period=self.params.slow_donchian_channel_period)
        self.atr = bt.indicators.ATR(period=self.params.trailing_stop_atr_period)
        # For trailing stop
        self.max_price = self.data.close[0]  # track the highest price after opening long positions
        self.min_price = self.data.close[0]  # track the lowest price after opening short positions

    def next(self):
        is_long = self.trend_filter_fast > self.trend_filter_slow  # trend filter

        # Position size rule
        max_loss = self.broker.getvalue() * self.p.risk_factor  # cash you afford to loss
        position_size = max_loss / self.atr

        # self.dc_slow.data_low <= self.dc_fast.data_low <= self.dc_fast.data_high <= self.dc_slow.data_high
        assert self.dc_slow.data_low <= self.dc_fast.data_low
        assert self.dc_fast.data_low <= self.dc_fast.data_high
        assert self.dc_fast.data_high <= self.dc_slow.data_high

        if self.data.close > self.dc_slow.data_high:
            if is_long and self.position.size == 0:
                self.long_order = self.buy(size=position_size)  # Entry rule 1
                print(f'Long {position_size}')
                self.max_price = self.data.close[0]
                return
        elif self.data.close > self.dc_fast.data_high:
            if self.position.size < 0:
                print(f'Close {self.position.size} by exit rule 2')
                self.close()  # Exit rule 2
                return
        elif self.data.close > self.dc_fast.data_low:
            pass
        elif self.data.close > self.dc_slow.data_low:
            if self.position.size > 0:
                print(f'Close {self.position.size} by exit rule 1')
                self.close()  # Exit rule 1
                return
        else:
            if (not is_long) and self.position.size == 0:
                self.short_order = self.sell(size=position_size)  # Entry rule 2
                print(f'Short {position_size}')
                self.min_price = self.data.close[0]
                return

        # Trailing stop
        if self.position.size > 0:
            self.max_price = max(self.max_price, self.data.close[0])
            if self.data.close[0] < (self.max_price - self.atr[0] * 3):
                print(f'Close {self.position.size}  by trailing stop rule')
                self.close()
                return
        if self.position.size < 0:
            self.min_price = min(self.max_price, self.data.close[0])
            if self.data.close[0] > (self.min_price + self.atr[0] * 3):
                print(f'Close {self.position.size} by trailing stop rule')
                self.close()
                return
