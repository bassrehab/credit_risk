import warnings

warnings.filterwarnings('ignore')
from pathlib import Path
import numpy as np
import pandas as pd
import talib
import logging
import matplotlib.pyplot as plt
import seaborn as sns


class AlphaFeatures:
    def __init__(self):
        sns.set_style('whitegrid')
        self.idx = pd.IndexSlice
        self.deciles = np.arange(.1, 1, .1).round(1)

    def loadHDF5Data(self, sourcefile='stock_prices.h5', destinationpath='..'):
        DATA_STORE = Path(destinationpath, 'data', sourcefile)
        with pd.HDFStore(DATA_STORE) as store:
            self.data = (store['us_stocks']
                         .loc[idx[:, '2006':'2016'],
                         :]  # slice 11 years from 2nd level of MultiIndex using pd.IndexSlice
                         .unstack('ticker')  # move first index level 'ticker' into the columns
                         .sort_index()
                         .fillna(method='ffill', limit=5)  # fill up to five days of missing data with latest
                         .stack('ticker')  # move Index level 'ticker' back into the rows
                         .swaplevel()  # swap levels of row index so we're back at (ticker, data)
                         .dropna()  # remove missing values
                         .sort_index())

            logging.debug(
                f"# Tickers: {len(data.index.unique('ticker')):,.0f} | # Dates: {len(data.index.unique('date')):,.0f}")

    def handleOutliers(self):
        daily_returns = self.data.groupby('ticker').close.pct_change()  # returns computed based on closing prices
        daily_returns.describe(percentiles=[.00001, .0001, .001, .999, .9999, .99999]).iloc[1:]
        outliers = daily_returns[(daily_returns < daily_returns.quantile(.00001)) |
                                 (daily_returns > daily_returns.quantile(.99999))]
        logging.debug(f'# Observations: {len(outliers):,.0f} | # Tickers: {len(outliers.index.unique("ticker")):,.0f}')
        self.data = self.data.drop(outliers.index.unique('ticker'), level='ticker')

    def getTopStocks(self, top, date):
        dv = self.data.close.mul(self.data.volume)
        topN = (dv.groupby(level='date')
                .rank(ascending=False)
                .unstack('ticker')
                .dropna(thresh=8 * 252, axis=1)
                .mean()
                .nsmallest(top))

        return topN

    def computeReturns(self, returnType):
        by_ticker = self.data.groupby(level='ticker')

        if returnType is 'HISTORICAL':
            T = [1, 3, 5, 10, 21, 42, 63, 126, 252]
            for t in T:
                self.data[f'ret_{t:02}'] = by_ticker.close.pct_change(t)  # compute returns for each ticker and period

        if returnType is 'FORWARD':
            self.data['ret_fwd'] = by_ticker.ret_01.shift(
                -1)  # shift returns back in time (tomorrow's returns are today's fwd returns)
            self.data = self.data.dropna(subset=['ret_fwd'])

    def bollingerBands(self, year='2012', price_type='close', ticker='AMZN', plot_graph=False, plot_nmri=False):
        _price = self.data.loc[idx[ticker, :], :].reset_index('ticker', drop=True)
        df = _price.loc[year, [price_type]]
        s = talib.BBANDS(df.close,  # Number of periods (2 to 100000)
                         timeperiod=20,
                         nbdevup=2,  # Deviation multiplier for lower band
                         nbdevdn=2,  # Deviation multiplier for upper band
                         matype=1  # default: SMA
                         )
        bb_bands = ['upper', 'middle', 'lower']

        df = _price.loc[year, [price_type]]
        df = df.assign(**dict(zip(bb_bands, s)))
        ax = df.loc[:, [year] + bb_bands].plot(figsize=(16, 5), lw=1)

        if plot_graph:
            ax.set_xlabel('')
            sns.despine()
            plt.tight_layout()

        if plot_nmri:
            self.plotNormalizedMeanReversionIndicators(df)
        return ax

    def plotNormalizedMeanReversionIndicators(self, df):
        fig, ax = plt.subplots(figsize=(16, 5))
        df.upper.div(df.close).plot(ax=ax, label='bb_up')
        df.lower.div(df.close).plot(ax=ax, label='bb_low')
        df.upper.div(df.lower).plot(ax=ax, label='bb_squeeze', rot=0)

        plt.legend()
        ax.set_xlabel('')
        sns.despine()
        plt.tight_layout()

    def compute_bb_indicators(self, close, timeperiod=20, matype=0):
        high, mid, low = talib.BBANDS(close,
                                      timeperiod=20,
                                      matype=matype)
        bb_up = high / close - 1  # normalize with respect to close
        bb_low = low / close - 1  # normalize with respect to close
        squeeze = (high - low) / close
        return pd.DataFrame({'BB_UP': bb_up,
                             'BB_LOW': bb_low,
                             'BB_SQUEEZE': squeeze},
                            index=close.index)

    def compute_sar_indicator(self, x, acceleration=.02, maximum=0.2):
        '''
        Normalized SAR indicator
        @param x:
        @param acceleration:
        @param maximum:
        @return:
        '''
        sar = talib.SAR(x.high,
                        x.low,
                        acceleration=acceleration,
                        maximum=maximum)
        return sar / x.close - 1

    def compute_adx(self, x, timeperiod=14):
        '''
        Average directional movement index (ADX)
        The ADX is the (simple) moving average of the absolute value of the difference between PLUS_DI and MINUS_DI,
        divided by their sum:
        @param timeperiod:
        @return:
        '''
        return talib.ADX(x.high,
                         x.low,
                         x.close,
                         timeperiod=timeperiod)

    def compute_adxr(self, x, timeperiod=14):
        '''
        Average Directional Movement Index Rating
        Averages the current ADX and the ADX T periods ago
        @param x:
        @param timeperiod:
        @return:
        '''
        return talib.ADXR(x.high,
                          x.low,
                          x.close,
                          timeperiod=timeperiod)

    def compute_stoch(self, x, fastk_period=14, slowk_period=3,
                      slowk_matype=0, slowd_period=3, slowd_matype=0):
        '''
        A stochastic oscillator is a momentum indicator comparing a particular closing price of a security to a
        range of its prices over a certain period of time. Stochastic oscillators are based on the idea that
        closing prices should confirm the trend.For stochastic (STOCH),
        there are four different lines: FASTK, FASTD, SLOWK and SLOWD.

        The D is the signal line usually drawn over its corresponding K function.

        @param x:
        @param fastk_period:
        @param slowk_period:
        @param slowk_matype:
        @param slowd_period:
        @param slowd_matype:
        @return:
        '''
        slowk, slowd = talib.STOCH(x.high, x.low, x.close,
                                   fastk_period=fastk_period,
                                   slowk_period=slowk_period,
                                   slowk_matype=slowk_matype,
                                   slowd_period=slowd_period,
                                   slowd_matype=slowd_matype)
        return slowd / slowk - 1

    def compute_ultosc(self, x, timeperiod1=7, timeperiod2=14, timeperiod3=28):
        '''
        The Ultimate Oscillator (ULTOSC), developed by Larry Williams, measures the average difference of the current
        close to the previous lowest price over three time frames (default: 7, 14, and 28) to avoid overreacting
        to short-term price changes and incorporat short, medium, and long-term market trends.

        It first computes the buying pressure,  BP𝑡 , then sums it over the three periods  𝑇1,𝑇2,𝑇3 ,
        normalized by the True Range.

        @param x:
        @param timeperiod1:
        @param timeperiod2:
        @param timeperiod3:
        @return:
        '''
        return talib.ULTOSC(x.high,
                            x.low,
                            x.close,
                            timeperiod1=timeperiod1,
                            timeperiod2=timeperiod2,
                            timeperiod3=timeperiod3)
