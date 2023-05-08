import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA

df = pd.read_csv('mock_data.csv', parse_dates=['Date'], index_col='Date')

df_resampled = df.resample('10T').mean()

df_filled = df.resample('10T').ffill()

print(df_filled)

model = ARIMA(df_filled['Yawns'], order=(1,3,0), seasonal_order=(24,0,0,48))
results = model.fit()

print(results.forecast(steps=10))
# plt.plot(df_resampled)
plt.plot(results.predict(start=len(df_filled), end=len(df_filled)+900))
plt.show()
