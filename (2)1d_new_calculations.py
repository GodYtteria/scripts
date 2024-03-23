import pandas as pd
import talib
import numpy as np
from openpyxl.styles import PatternFill
from openpyxl import Workbook


class TA:
    def __init__(self):
        # Initialize parameters for technical indicators
        self.MAfast = 10
        self.MAslow = 20
        self.MACDfast = 12
        self.MACDslow = 26
        self.MACDsignal = 9
        self.ATRperiod = 6
        self.ATRfactor = 2
        self.ADXperiod = 14
        self.ADXshift = 14
        self.DIperiod = 14
        self.Engulfperiod = 10
        self.RSIperiod = 14
        self.RSIupper = 70
        self.RSIlower = 30
        self.DemarkLookback = 10

    def MA(self, close):
        # Moving Average (MA) calculation
        print("Calculating Moving Average...")
        output = close.copy()
        df = talib.MA(close, self.MAfast) - talib.MA(close, self.MAslow)
        df[df > 0] = 1
        df[df < 0] = -1
        print("Moving Average calculation successful.")
        return df
        

    def MACD(self, close):
        # Moving Average Convergence Divergence (MACD) calculation
        print("Calculating MACD...")
        return talib.MACD(close, self.MACDfast, self.MACDslow, self.MACDsignal)
        print("MACD calculation successful.")

    def LL(self, macd, signal):
        # Logic for identifying bullish or bearish MACD signal
        return (macd > signal) & (signal > 0)

    def Trender(self, h, l, c):
        # Trend calculation based on ATR (Average True Range)
        atr = self.ATRfactor * talib.ATR(h, l, c, self.ATRperiod)
        up = 0.5 * (h + l) + atr
        down = up - 2 * atr
        st = down.copy()
        trend = down.copy()
        trend.iloc[:] = 1
        for i in range(1, c.shape[0]):
            if c.iloc[i] > st.iloc[i - 1] and trend.iloc[i - 1] < 0:
                trend.iloc[i] = 1
                st.iloc[i] = down.iloc[i]
            elif c.iloc[i] < st.iloc[i - 1] and trend.iloc[i - 1] > 0:
                trend.iloc[i] = -1
                st.iloc[i] = up.iloc[i]
            elif trend.iloc[i - 1] > 0:
                trend.iloc[i] = 1
                st.iloc[i] = max(down.iloc[i], st.iloc[i - 1])
            else:
                trend.iloc[i] = -1
                st.iloc[i] = min(up.iloc[i], st.iloc[i - 1])
        return trend

    def ADX(self, h, l, c):
        # Average Directional Movement Index (ADX) calculation
        adx = talib.ADX(h, l, c, self.ADXperiod)
        adx = (adx - adx.shift(self.ADXshift)) / 2
        adx[adx > 0] = 1
        adx[adx < 0] = -1
        return adx

    def DMI(self, h, l ,c):
        # Directional Movement Index (DMI) calculation
        pdi = talib.PLUS_DI(h, l, c, self.DIperiod)
        mdi = talib.MINUS_DI(h, l, c, self.DIperiod)
        dmi = pdi - mdi
        dmi[dmi > 0] = 1
        dmi[dmi < 0] = -1
        return dmi

    def Engulf_original(self, o, h, l, c):
        # Original engulfing pattern calculation
        black = c < o
        white = c > o
        engulf = (h > h.shift(1)) & (l < l.shift(1))
        bullEngulf = (white & black.shift(1) & engulf).astype(int)
        bearEngulf = (black & white.shift(1) & engulf).astype(int)
        sumBull = bullEngulf.rolling(self.Engulfperiod).sum()
        sumBear = bearEngulf.rolling(self.Engulfperiod).sum()
        netEngulf = 0.5 * (sumBull - sumBear)
        netEngulf[netEngulf >= 0.5] = 1
        netEngulf[netEngulf <= -0.5] = -1
        return netEngulf

    def Engulf(self, data, o, h, l, c):
        # Customized engulfing pattern calculation
        df = data[['OPEN', 'HIGH', 'LOW', 'CLOSE']].copy()
        black = c < o
        white = c > o
        engulf = (h > h.shift(1)) & (l < l.shift(1))
        bullEngulf = (white & black.shift(1) & engulf).astype(int)
        bearEngulf = (black & white.shift(1) & engulf).astype(int)

        df['bullEngulf'] = bullEngulf
        df['bullEngulfScore'] = 0
        df['bearEngulf'] = bearEngulf
        df['bearEngulfScore'] = 0
        df['engulf_score'] = 0

        for i in range(len(df)):
            # Calculate scores for bullish and bearish engulfing patterns
            if df['bullEngulf'][i] == 1:
                bull_high = df['HIGH'][i]
                bull_low = df['LOW'][i]
                for j in range(i + 1, min(i + 11, len(df))):
                    if df['CLOSE'][j] < bull_high and df['CLOSE'][j] > bull_low:
                        df.loc[df.index[j], 'bullEngulfScore'] = -1
                    if df['CLOSE'][j] > bull_high and df['CLOSE'][j] > df['CLOSE'][j - 1]:
                        df.loc[df.index[j], 'bullEngulfScore'] = -2
                    if df['bullEngulfScore'][j - 1] == -2 and df['bullEngulfScore'][j] != -2:
                        df.loc[df.index[j], 'bullEngulfScore'] = 0
                        break
                    if df['CLOSE'][j] < bull_low:
                        df.loc[df.index[j], 'bullEngulfScore'] = 0
                        break

            if df['bearEngulf'][i] == 1:
                bear_high = df['HIGH'][i]
                bear_low = df['LOW'][i]
                for j in range(i + 1, min(i + 11, len(df))):
                    if df['CLOSE'][j] < bear_high and df['CLOSE'][j] > bear_low:
                        df.loc[df.index[j], 'bearEngulfScore'] = 1
                    if df['CLOSE'][j] < bear_low and df['CLOSE'][j] < df['CLOSE'][j - 1]:
                        df.loc[df.index[j], 'bearEngulfScore'] = 2
                    if df['bearEngulfScore'][j - 1] == 2 and df['bearEngulfScore'][j] != 2:
                        df.loc[df.index[j], 'bearEngulfScore'] = 0
                        break
                    if df['CLOSE'][j] > bear_high:
                        df.loc[df.index[j], 'bearEngulfScore'] = 0
                        break

            df['engulf_score'][i] = df['bullEngulfScore'][i] + df['bearEngulfScore'][i]

        engulf_score = df['engulf_score']
        return engulf_score

    def RSI(self, close):
        # Relative Strength Index (RSI) calculation
        rsi = talib.RSI(close, self.RSIperiod)
        rsi_ma = talib.MA(rsi, timeperiod=5)
        rsi_score = pd.Series(0, index=rsi.index)

        for i in range(1, len(rsi)):  # Start from 1 to avoid accessing -1 index
            # Modified conditions to correctly assign scores
            if rsi.iloc[i] > self.RSIupper or (rsi.iloc[i] > rsi_ma.iloc[i] and rsi.iloc[i - 1] <= rsi_ma.iloc[i - 1]):
                rsi_score.iloc[i] = 1
            elif rsi.iloc[i] < self.RSIlower or (rsi.iloc[i] < rsi_ma.iloc[i] and rsi.iloc[i - 1] >= rsi_ma.iloc[i - 1]):
                rsi_score.iloc[i] = -1
            # Added conditions to handle crossovers
            if rsi.iloc[i] > 70 and rsi.iloc[i] < rsi_ma.iloc[i] and rsi.iloc[i - 1] > rsi_ma.iloc[i - 1]:
                rsi_score.iloc[i] = 2
            elif rsi.iloc[i] < 30 and rsi.iloc[i] > rsi_ma.iloc[i] and rsi.iloc[i - 1] < rsi_ma.iloc[i - 1]:
                rsi_score.iloc[i] = -2
        return rsi_score


    def Demark(self, h, l, close):
        # Demark Indicator calculation
        s = close - close.shift(4)

        setup = close.copy()
        setup.iloc[0] = 0
        count = 0

        for i in range(1, close.shape[0]):
            # Counting setup trend
            if s.iloc[i] < 0 and s.iloc[i - 1] < 0:
                if count < 0:
                    count -= 1
                else:
                    count = -1
            elif s.iloc[i] > 0 and s.iloc[i - 1] > 0:
                if count > 0:
                    count += 1
                else:
                    count = 1
            else:
                count = 0
            setup.iloc[i] = count

        countdown = close.copy()
        countdown.iloc[0] = 0
        count = 0

        for i in range(1, close.shape[0]):
            # Counting countdown trend
            if setup.iloc[i - 1] == 9:
                count = 1
            if setup.iloc[i - 1] == -9:
                count = -1

            if setup.iloc[i] > 0 and count > 0 and close.iloc[i] > h.iloc[i - 2]:
                count += 1

                if setup.iloc[i] < 0:
                    count = 0

            if setup.iloc[i] < 0 and count < 0 and close.iloc[i] < l.iloc[i - 2]:
                count -= 1

                if setup.iloc[i] > 0:
                    count = 0

            countdown.iloc[i] = count

        demark_score = pd.Series(0, index=close.index)
        up = np.nan
        down = np.nan
        up_line = pd.Series(np.nan, index=close.index)
        down_line = pd.Series(np.nan, index=close.index)

        for i in range(1, close.shape[0]):
            # Calculating demark scores and trend lines
            if setup.iloc[i] == 9 or countdown.iloc[i] == 13:
                demark_score[i] = 1
            if setup.iloc[i] == -9 or countdown.iloc[i] == -13:
                demark_score[i] = -1

            if setup.iloc[i] == 9:
                up = close[i]
                up_line[i] = up
            else:
                up_line[i] = up

            if setup.iloc[i] == -9:
                down = close[i]
                down_line[i] = down
            else:
                down_line[i] = down

            if setup.iloc[i] > 9 or countdown.iloc[i] > 13:
                if close[i] < up_line[i]:
                    demark_score[i] = 2
            if setup.iloc[i] < -9 or countdown.iloc[i] < -13:
                if close[i] > down_line[i]:
                    demark_score[i] = -2
        return demark_score


ta = TA()

# Read the data from the CSV file
df = pd.read_csv('1d_crypto_data.csv')

# Renaming columns for consistency
df.rename(columns={'Open': 'OPEN', 'High': 'HIGH', 'Low': 'LOW', 'Close': 'CLOSE'}, inplace=True)
df['OPEN'] = df['OPEN'].astype(float)
df['HIGH'] = df['HIGH'].astype(float)
df['LOW'] = df['LOW'].astype(float)
df['CLOSE'] = df['CLOSE'].astype(float)

# Calculate technical indicators and append to the dataframe
df['MA'] = ta.MA(df['CLOSE'])
macd, macdsignal, macdhist = ta.MACD(df['CLOSE'])
df['MACD'] = macd
df['MACDSignal'] = macdsignal
df['MACDHist'] = macdhist
df['LL'] = ta.LL(df['MACD'], df['MACDSignal'])
df['Trender'] = ta.Trender(df['HIGH'], df['LOW'], df['CLOSE'])
df['ADX'] = ta.ADX(df['HIGH'], df['LOW'], df['CLOSE'])
df['DMI'] = ta.DMI(df['HIGH'], df['LOW'], df['CLOSE'])
df['Engulf'] = ta.Engulf(df, df['OPEN'], df['HIGH'], df['LOW'], df['CLOSE'])
df['RSI'] = ta.RSI(df['CLOSE'])
df['Demark'] = ta.Demark(df['HIGH'], df['LOW'], df['CLOSE'])

# Calculate the 'score' based on your indicators
df['score'] = (
    df['MA'] +
    df['LL'] +
    df['Trender'] +
    df['ADX'] +
    df['DMI'] +
    df['Engulf'] +
    df['RSI'] +
    df['Demark']
)

conditions_signal = [
    (df['score'] >= 4.5),                # Strong Buy
    (df['score'] >= 3) & (df['score'] < 4.5),   # Buy
    (df['score'] >= -1.5) & (df['score'] < 3),  # Neutral
    (df['score'] >= -3.5) & (df['score'] < -1.5),  # Sell
    (df['score'] < -3.5),                # Strong Sell
]

choices_signal = [
    'Strong Buy',    # for scores greater than or equal to 4.5
    'Buy',           # for scores 3 to less than 4.5
    'Neutral',       # for scores -1.5 to less than 3
    'Sell',          # for scores -3.5 to less than -1.5
    'Strong Sell'    # for scores less than -3.5
]

# Assign signals based on the score
df['Signal'] = np.select(conditions_signal, choices_signal, default='Neutral')

# New scoring for extreme conditions
conditions_extreme = [
    (df['score'] == 6),  # Overbought
    (df['score'] == 5),  # Overbought
    (df['score'] == 4),  # Overbought
    (df['score'] >= 1) & (df['score'] <= 3),  # Neutral
    (df['score'] == 0),  # Neutral
    (df['score'] <= -1) & (df['score'] >= -3),  # Neutral
    (df['score'] == -4),  # Oversold
    (df['score'] == -5),  # Oversold
    (df['score'] == -6),  # Oversold
]

choices_extreme = [
    'Overbought',   # for score 6
    'Overbought',   # for score 5
    'Overbought',   # for score 4
    'Neutral',      # for scores 1 to 3
    'Neutral',      # for score 0
    'Neutral',      # for scores -1 to -3
    'Oversold',     # for score -4
    'Oversold',     # for score -5
    'Oversold',     # for score -6
]

# Assign extreme signals based on the score
df['Extreme Signal'] = np.select(conditions_extreme, choices_extreme, default='Neutral')

# Save the updated dataframe to a new CSV file
df.to_csv('1d_Crypto_Monitor_List.csv', index=False)
print(df['score'].unique())

print("Done")

