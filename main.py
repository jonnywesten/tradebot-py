import datetime
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas_datareader.data as web
from dateutil.relativedelta import relativedelta

matplotlib.use('TkAgg')

start = datetime.datetime.now() - relativedelta(years=1)

amzn = web.DataReader("AMZN", "yahoo", start)
close = amzn['Close']
close.plot()
plt.show()
