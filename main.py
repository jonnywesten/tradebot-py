import datetime
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas_datareader.data as web
from dateutil.relativedelta import relativedelta

matplotlib.use('TkAgg')

start = datetime.datetime.now() - relativedelta(years=5)

df = web.DataReader("^GSPC", "yahoo", start)
print(df)
close = df['Adj Close']
volume = df['Volume']

plt.subplot(1, 2, 1)
plt.plot(close)
plt.subplot(1, 2, 2)
plt.plot(volume)
plt.show()
