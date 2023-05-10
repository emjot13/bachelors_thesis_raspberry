import copy
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM, Dropout
import statsmodels.api as sm
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt

# Wczytanie danych
df = pd.read_csv('mock_data.csv', parse_dates=['Date'], index_col='Date')

# Użycie kolumny 'Yawns' jako źródła danych
df = df[['Yawns']]




# Podział na dane treningowe i testowe
train_size = int(len(df) * 0.8)
train_data, test_data = df.iloc[:train_size], df.iloc[train_size:]

# Normalizacja danych
scaler = MinMaxScaler()
train_data = scaler.fit_transform(train_data)
test_data = scaler.transform(test_data)


def create_dataset(dataset, time_steps=1):
    X, y = [], []
    for i in range(len(dataset) - time_steps):
        X.append(dataset[i:i + time_steps])
        y.append(dataset[i + time_steps])
    return np.array(X), np.array(y)


time_steps = 30
X_train, y_train = create_dataset(train_data, time_steps)
X_test, y_test = create_dataset(test_data, time_steps)

# Dopasowanie struktury danych do modelu
X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))
X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))

# Definicja modelu
model = Sequential()
model.add(LSTM(units=50, return_sequences=True, input_shape=(X_train.shape[1], 1)))
model.add(Dropout(0.2))
model.add(LSTM(units=50, return_sequences=True))
model.add(Dropout(0.2))
model.add(LSTM(units=50))
model.add(Dropout(0.2))
model.add(Dense(units=1))

model.compile(optimizer='adam', loss='mean_squared_error')

# Trenowanie modelu
model.fit(X_train, y_train, epochs=2, batch_size=32)

# Przewidywanie przyszlych danych
y_pred = model.predict(X_test)
y_pred = scaler.inverse_transform(y_pred)

# Wykres z danymi przewidzianymi i prawdziwymi

plt.plot(df.values[:18000], label='True Values')
plt.plot(y_pred, label='Predicted Values')
plt.legend()
plt.show()

