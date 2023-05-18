import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import datetime
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM, Dropout
import matplotlib.pyplot as plt

# Wczytanie danych
loaded_df = pd.read_csv('mock_data.csv', parse_dates=['Date'])


def convert_to_day_progress(date):
    day_progress = ((date.hour * 60 * 60) + (date.minute * 60) + date.second - (8 * 60 * 60)) / (8 * 60 * 60)
    return day_progress


def get_weekday(date):
    day = date.weekday()
    return day


# Użycie kolumny 'Date' i 'Yawns' jako źródła danych
df = loaded_df[["Date", 'Yawns']]

# Dodanie dni tygodnia i day_progress
df["Weekday"] = df["Date"].apply(get_weekday)
df["Day_progress"] = df["Date"].apply(convert_to_day_progress)
df = df[["Day_progress", "Yawns", "Weekday"]]

# Zipowanie danych w strukture [(day_progress, weekday)...]
X = list(zip(df["Day_progress"].values, df["Weekday"].values))
y = df["Yawns"].values

# Normalizacja danych
scaler = MinMaxScaler()
X = scaler.fit_transform(X)
print(X)
X = np.reshape(X, (X.shape[0], X.shape[1], 1))
# Podział na dane treningowe i testowe
X_train = X[:int(len(X) * 0.8)]
X_test = X[int(len(X) * 0.8):]
y_train = y[:int(len(y) * 0.8)]
y_test = y[int(len(y) * 0.8):]

# Ustawienie modelu
model = Sequential()
model.add(LSTM(units=128, return_sequences=True, input_shape=(X_train.shape[1], X_train.shape[2])))
model.add(Dropout(0.2))
model.add(LSTM(units=64, return_sequences=True))
model.add(Dropout(0.2))
model.add(LSTM(units=32))
model.add(Dropout(0.2))
model.add(Dense(units=1))

model.compile(optimizer='adam', loss='mean_squared_error')

# Trenowanie modelu
model.fit(X_train, y_train, epochs=10, batch_size=10)

# Przewidywanie danych
y_pred = model.predict(X_test[220:1150])
y_pred = np.round(y_pred, 0)

# Wykres przewidzianych i prawdziwych danych
plt.plot(y_test[220:1150], label='True Values')
plt.plot(y_pred, label='Predicted Values')
plt.legend()
plt.show()
