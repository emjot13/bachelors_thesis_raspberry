import pandas as pd
from keras.saving.saving_api import load_model
from sklearn.preprocessing import MinMaxScaler
import datetime
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM, Dropout
import matplotlib.pyplot as plt


# Wczytanie danych


def convert_date_to_day_progress(date):
    day_progress = ((date.hour * 60 * 60) + (date.minute * 60) + date.second - (8 * 60 * 60)) / (8 * 60 * 60)
    return day_progress


def convert_tick_to_day_progress(tick, tick_interval=30):
    return tick / (8 * 60 * (60 / tick_interval))


def get_weekday(date):
    day = date.weekday()
    return day


def train_model():
    loaded_df = pd.read_csv('mock_data.csv', parse_dates=['Date'])
    # Użycie kolumny 'Date' i 'Yawns' jako źródła danych
    df = loaded_df[["Date", 'Yawns']]

    # Dodanie dni tygodnia i day_progress
    df["Weekday"] = df["Date"].apply(get_weekday)
    df["Day_progress"] = df["Date"].apply(convert_date_to_day_progress)
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
    model.fit(X_train, y_train, epochs=8, batch_size=30)

    model.save("fatigue_model.h5")


def generate_day_ticks(date, shift_length=8, tick_interval=30):
    start_tick = int((date.hour - shift_length) * 60 * (60 / tick_interval))
    end_tick = int(start_tick + (shift_length * 60 * (60 / tick_interval)))
    arr = [i for i in range(start_tick, end_tick)]
    return arr


# print(generate_day_ticks(datetime.datetime(2023, 10, 10, 8)))


def predict_day(date):
    weekday = get_weekday(date)
    ticks = generate_day_ticks(date)
    X_vals = [[convert_tick_to_day_progress(i), weekday] for i in ticks]
    print(X_vals)
    model = load_model("fatigue_model.h5")
    # Przewidywanie danych
    y_pred = model.predict(X_vals)
    # y_pred = np.round(y_pred, 0)

    # Wykres przewidzianych i prawdziwych danych
    plt.plot(y_pred, label='Predicted Values')
    plt.legend()
    plt.show()

predict_day(datetime.datetime(2023,10,10,8))
