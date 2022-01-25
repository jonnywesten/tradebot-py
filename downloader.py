import numpy as np
import datetime as dt  # For datetime objects
import pandas_datareader.data as web
from dateutil.relativedelta import relativedelta
import pandas as pd
import os


def downloadSPY():
    folderName = 'data/' + dt.datetime.today().strftime('%Y-%m-%d')
    os.makedirs(folderName, exist_ok=True)

    start = dt.datetime.now() - relativedelta(years=5)
    end = dt.datetime.now() - relativedelta(years=0)

    payload = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')

    df = payload[0]

    symbols = df['Symbol'].values.tolist()
    # stocks = np.concatenate((['^GSPC'], symbols))
    print('downloading...')

    for s in symbols:
        print(s)
        fileName = folderName + '/' + s
        if not os.path.isfile(fileName):
            try:
                df = web.DataReader(s, "yahoo", start, end)
                df.to_csv(fileName)
            except:
                print('cannot download', s)

    print('done...')


if __name__ == '__main__':
    # runStrategySingle(BuyAndHold, plot=False)
    downloadSPY()
