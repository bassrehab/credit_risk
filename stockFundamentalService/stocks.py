# Created by Subhadip Mitra <dev@subhadipmitra.com>
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.pyplot as plt

class Stocks:
    _baseDF = None

    def __init__(self):
        pass

    def loadSourceData(self, filename):
        df = pd.read_csv(filename, parse_dates=['date'], index_col=['ticker', 'date'])
        self._baseDF = (df.loc[idx[:, '2000':], :]
                        .filter(like='adj')
                        .rename(columns=lambda x: x.replace('adj_', '')).dropna())

    def plotSymbol(self, df, symbol='TDC'):
        fig, axes = plt.subplots(nrows=2, figsize=(14, 6), sharex=True)
        s = df.loc[symbol, 'close']
        s.plot(rot=0, ax=axes[0], title=f'{symbol} Close Price')
        s.pct_change().plot(rot=0, ax=axes[1], title=f'{symbol} Daily Returns')
        axes[1].set_xlabel('')
        sns.despine()
        fig.tight_layout()


    def writeHDF5(self, df, label, outfile='../data/stock_prices.h5'):
        df.to_hdf(outfile, label)




class testZipline:
    def initialize(self, context):
        context.i = 0
        context.asset = symbol('AAPL')

    def handle_data(self, context, data):
        # Skip first 300 days to get full windows
        context.i += 1
        if context.i < 300:
            return

        # Compute averages
        # data.history() has to be called with the same params
        # from above and returns a pandas dataframe.
        short_mavg = data.history(context.asset, 'price', bar_count=100, frequency="1d").mean()
        long_mavg = data.history(context.asset, 'price', bar_count=300, frequency="1d").mean()

        # Trading logic
        if short_mavg > long_mavg:
            # order_target orders as many shares as needed to
            # achieve the desired number of shares.
            order_target(context.asset, 100)
        elif short_mavg < long_mavg:
            order_target(context.asset, 0)

        # Save values for later inspection
        record(AAPL=data.current(context.asset, 'price'),
               short_mavg=short_mavg,
               long_mavg=long_mavg)

    def analyze(self, context, perf):
        fig = plt.figure()
        ax1 = fig.add_subplot(211)
        perf.portfolio_value.plot(ax=ax1)
        ax1.set_ylabel('portfolio value in $')

        ax2 = fig.add_subplot(212)
        perf['AAPL'].plot(ax=ax2)
        perf[['short_mavg', 'long_mavg']].plot(ax=ax2)

        perf_trans = perf.ix[[t != [] for t in perf.transactions]]
        buys = perf_trans.ix[[t[0]['amount'] > 0 for t in perf_trans.transactions]]
        sells = perf_trans.ix[
            [t[0]['amount'] < 0 for t in perf_trans.transactions]]
        ax2.plot(buys.index, perf.short_mavg.ix[buys.index],
                 '^', markersize=10, color='m')
        ax2.plot(sells.index, perf.short_mavg.ix[sells.index],
                 'v', markersize=10, color='k')
        ax2.set_ylabel('price in $')
        plt.legend(loc=0)
        plt.show()
