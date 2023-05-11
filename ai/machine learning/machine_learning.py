import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM, Dropout
import matplotlib.pyplot as plt
from generate_mock_data import generate_one_day



# Load the data
df = pd.read_csv('mock_data.csv')

# Convert the 'Date' column to a datetime object and set it as the index
df['Date'] = pd.to_datetime(df['Date'])
df.set_index('Date', inplace=True)

# Normalize the data
df_norm = (df - df.mean()) / df.std()

# Split the data into sequences of length 32
seq_length = 32
data = []
for i in range(len(df_norm) - seq_length):
    data.append(df_norm.iloc[i:i+seq_length].values)

# Convert the data to numpy arrays
data = np.array(data)

# Split the data into training and validation sets
train_size = int(len(data) * 0.8)
train_data = data[:train_size]
val_data = data[train_size:]

# Separate the inputs (day progress) from the outputs (yawns increase)
x_train = train_data[:, :, -1].reshape(train_size, seq_length, 1)
y_train = train_data[:, :, 3].reshape(train_size, seq_length, 1)
x_val = val_data[:, :, -1].reshape(len(val_data), seq_length, 1)
y_val = val_data[:, :, 3].reshape(len(val_data), seq_length, 1)


# Define the model architecture
model = Sequential()
model.add(LSTM(64, input_shape=(seq_length, 1), return_sequences=True))
model.add(Dense(1))

# Compile the model
model.compile(loss='mse', optimizer='adam')

# Train the model
history = model.fit(x_train, y_train, epochs=2, batch_size=64, validation_data=(x_val, y_val))

seed = df_norm.iloc[-seq_length:].values.reshape(1, seq_length, -1)

# Make predictions for the next 32 ticks
preds = []
for i in range(32):
    pred = model.predict(seed)
    preds.append(pred)
    seed = np.concatenate([seed[:, 1:, :], pred.reshape(1, 1, -1)], axis=1)

# Denormalize the predictions
preds = np.array(preds).reshape(-1, 1)
preds = preds * df.std()[3] + df.mean()[3]

# Plot the predicted values for the next day
import matplotlib.pyplot as plt

plt.plot(df.index[-seq_length:], df['Yawns_increase'].iloc[-seq_length:], label='True Values')
plt.plot(pd.date_range(start=df.index[-1], periods=32, freq='30s'), preds, label='Predicted Values')
plt.legend()
plt.show()




# Wczytanie danych
# df = pd.read_csv('mock_data.csv', parse_dates=['Date'])
#
# # Użycie kolumny 'Yawns' jako źródła danych
# df = df[['Yawns', 'Day_progress']]
#
# # Podział na dane treningowe i testowe
# train_size = int(len(df) * 0.8)
# train_data, test_data = df.iloc[:train_size], df.iloc[train_size:]
#
# # Normalizacja danych
# scaler = MinMaxScaler()
# train_data = scaler.fit_transform(train_data)
# test_data = scaler.transform(test_data)
#
#
# def create_dataset(dataset, time_steps=1, n_features=1):
#     X, y = [], []
#     for i in range(len(dataset) - time_steps):
#         X.append(dataset[i:i + time_steps])
#         y.append(dataset[i + time_steps])
#     X, y = np.array(X), np.array(y)
#     X = X.reshape((X.shape[0], X.shape[1], n_features))
#     return X, y
#
#
# time_steps = 30
# X_train, y_train = create_dataset(train_data, time_steps, n_features=2)
# X_test, y_test = create_dataset(test_data, time_steps, n_features=2)
#
# # X_train, y_train = create_dataset(train_data, time_steps)
# # X_test, y_test = create_dataset(test_data, time_steps)
#
#
# # Dopasowanie struktury danych do modelu
# # X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 2))
# # X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 2))
#
# # print(f"1{X_test[0]}")
# # print(f"2{X_test[1]}")
# # print(f"3{X_test[2]}")
#
# # Ustawienie modelu
#
# model = Sequential()
# model.add(LSTM(32, input_shape=(time_steps, 2)))
# model.add(Dense(2))
# model.compile(optimizer='adam', loss='mse')
#
# # Trenowanie modelu
# model.fit(X_train, y_train, epochs=1, batch_size=32, validation_data=(X_test, y_test))
#
#
# def generate_next_day_sample_data_points(tick_interval=30):
#     ticks = generate_one_day()[0]
#     yawns = generate_one_day()[1]
#     day_progress_values = []
#     for tick in ticks:
#         day_progress = tick / (8 * 60 * (60 / tick_interval))
#         day_progress_values.append(day_progress)
#
#     return yawns, day_progress_values
#
#
# # Generate sample data
# X_new = generate_next_day_sample_data_points()  # array of day_progress values for the next day
# X_new = np.array(X_new).reshape((32, 30, 2))
# y_pred = model.predict(X_new)
# y_pred = np.reshape(y_pred, (y_pred.shape[0], 2))
# y_pred = scaler.inverse_transform(y_pred)
#
#
# # Przewidywanie przyszlych danych
# # y_pred = model.predict(X_test)
# # y_pred = scaler.inverse_transform(y_pred)
#
# # Wykres z danymi przewidzianymi i prawdziwymi
#
# print(y_pred)
#
# plt.plot(df.values[0], df.values[1], label='True Values')
# plt.plot(df.values[0], y_pred[0,:], label='Predicted Values')
# plt.legend()
# plt.show()
