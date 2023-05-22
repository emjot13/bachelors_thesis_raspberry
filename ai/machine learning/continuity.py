import pandas as pd
from keras.saving.saving_api import load_model
from sklearn.preprocessing import MinMaxScaler
import datetime
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM, Dropout
import matplotlib.pyplot as plt


def convert_to_day_progress(date):
    day_progress = ((date.hour * 60 * 60) + (date.minute * 60) + date.second - (8 * 60 * 60)) / (8 * 60 * 60)
    return day_progress


def convert_tick_to_day_progress(tick, tick_interval=30):
    return tick / (8 * 60 * (60 / tick_interval))


def get_weekday(date):
    day = date.weekday()
    return day


def train_model():
    # Wczytanie danych
    loaded_df = pd.read_csv('mock_data.csv', parse_dates=['Date'])
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


    # Ustawienie modelu
    model = Sequential()
    model.add(LSTM(units=128, return_sequences=True, input_shape=(X.shape[1], X.shape[2])))
    model.add(Dropout(0.2))
    model.add(LSTM(units=64, return_sequences=True))
    model.add(Dropout(0.2))
    model.add(LSTM(units=32))
    model.add(Dropout(0.2))
    model.add(Dense(units=1))

    model.compile(optimizer='adam', loss='mean_squared_error')

    # Trenowanie modelu
    model.fit(X, y, epochs=3, batch_size=120)

    model.save("continuity_model.h5")


# train_model()

def generate_rest_of_day_ticks(date, end_hour=16, tick_interval=30):
    start_tick = int((date.hour - 8) * 60 * (60 / tick_interval) + date.minute * (60 / tick_interval) + (
                date.second / tick_interval))
    end_tick = int((end_hour - 8) * 60 * (60 / tick_interval))
    arr = [i for i in range(start_tick, end_tick + 1)]
    return arr


# przewiduje zmeczenie do konca dnia, zgodnie z dotychczasowym zmeczeniem
# ticks_data musi byc tablica obiektow w formacie JSON
# np. [{"Date": "2023-01-10 08:00:00", "Yawns": ..., ...},...]
# Można pomyśleć o zmianie na użycie tylko ostatniego dostępnego ticka, bo i tak model nie jest trenowany na tych danych
# Poprzednie dane sa uzywane jedynie do wykresu
def predict_rest_of_day(ticks_data, end_hour=16):
    # Generuje ticki do końca dnia, i przewiduje na nich zmęczenie, następnie dopasowuje wygenerowane do dotychczas
    # zarejestrowanych ziewnięć
    yawns_data = [tick["Yawns"] for tick in ticks_data]
    last_tick = ticks_data[-1]
    weekday = get_weekday(datetime.datetime.strptime(last_tick["Date"], "%Y-%m-%d %H:%M:%S"))
    new_ticks = generate_rest_of_day_ticks(datetime.datetime.strptime(last_tick["Date"], "%Y-%m-%d %H:%M:%S"), end_hour)
    X_vals = [[convert_tick_to_day_progress(i), weekday] for i in new_ticks]
    model = load_model("continuity_model.h5")
    # Przewidywanie danych
    y_pred_current_day = model.predict(X_vals)

    last_real_yawn = yawns_data[-1]

    # Dopasowanie predykcji do dotychczasowych danych
    if y_pred_current_day[0] < last_real_yawn:
        y_pred_current_day += (last_real_yawn - y_pred_current_day[0])
    else:
        y_pred_current_day += (last_real_yawn - y_pred_current_day[0] + 1)

    y_pred_current_day = np.concatenate([yawns_data, y_pred_current_day.flatten()])

    # Wykres przewidzianych danych
    plt.plot(y_pred_current_day, label='Predicted Values')
    plt.legend()
    plt.show()


predict_rest_of_day([
    {
        "Date": "2023-01-10 08:00:00",
        "Yawns": 0,
        "Sleeps": 0,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:00:30",
        "Yawns": 0,
        "Sleeps": 0,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:01:00",
        "Yawns": 1,
        "Sleeps": 0,
        "Yawns_increase": 1,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:01:30",
        "Yawns": 1,
        "Sleeps": 1,
        "Yawns_increase": 0,
        "Sleeps_increase": 1
    },
    {
        "Date": "2023-01-10 08:02:00",
        "Yawns": 1,
        "Sleeps": 1,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:02:30",
        "Yawns": 1,
        "Sleeps": 1,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:03:00",
        "Yawns": 1,
        "Sleeps": 1,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:03:30",
        "Yawns": 1,
        "Sleeps": 1,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:04:00",
        "Yawns": 1,
        "Sleeps": 1,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:04:30",
        "Yawns": 1,
        "Sleeps": 1,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:05:00",
        "Yawns": 1,
        "Sleeps": 1,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:05:30",
        "Yawns": 1,
        "Sleeps": 1,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:06:00",
        "Yawns": 1,
        "Sleeps": 1,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:06:30",
        "Yawns": 1,
        "Sleeps": 1,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:07:00",
        "Yawns": 1,
        "Sleeps": 1,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:07:30",
        "Yawns": 1,
        "Sleeps": 1,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:08:00",
        "Yawns": 1,
        "Sleeps": 1,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:08:30",
        "Yawns": 1,
        "Sleeps": 1,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:09:00",
        "Yawns": 1,
        "Sleeps": 1,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:09:30",
        "Yawns": 1,
        "Sleeps": 1,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:10:00",
        "Yawns": 1,
        "Sleeps": 1,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:10:30",
        "Yawns": 1,
        "Sleeps": 1,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:11:00",
        "Yawns": 1,
        "Sleeps": 1,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:11:30",
        "Yawns": 1,
        "Sleeps": 1,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:12:00",
        "Yawns": 1,
        "Sleeps": 1,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:12:30",
        "Yawns": 1,
        "Sleeps": 1,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:13:00",
        "Yawns": 1,
        "Sleeps": 1,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:13:30",
        "Yawns": 1,
        "Sleeps": 1,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:14:00",
        "Yawns": 1,
        "Sleeps": 1,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:14:30",
        "Yawns": 1,
        "Sleeps": 1,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:15:00",
        "Yawns": 1,
        "Sleeps": 1,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:15:30",
        "Yawns": 1,
        "Sleeps": 1,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:16:00",
        "Yawns": 1,
        "Sleeps": 1,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:16:30",
        "Yawns": 1,
        "Sleeps": 1,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:17:00",
        "Yawns": 1,
        "Sleeps": 1,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:17:30",
        "Yawns": 1,
        "Sleeps": 1,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:18:00",
        "Yawns": 1,
        "Sleeps": 1,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:18:30",
        "Yawns": 1,
        "Sleeps": 1,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:19:00",
        "Yawns": 1,
        "Sleeps": 1,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:19:30",
        "Yawns": 2,
        "Sleeps": 1,
        "Yawns_increase": 1,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:20:00",
        "Yawns": 2,
        "Sleeps": 1,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:20:30",
        "Yawns": 2,
        "Sleeps": 1,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:21:00",
        "Yawns": 2,
        "Sleeps": 1,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:21:30",
        "Yawns": 2,
        "Sleeps": 1,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:22:00",
        "Yawns": 2,
        "Sleeps": 1,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:22:30",
        "Yawns": 2,
        "Sleeps": 1,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:23:00",
        "Yawns": 2,
        "Sleeps": 1,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:23:30",
        "Yawns": 2,
        "Sleeps": 1,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:24:00",
        "Yawns": 2,
        "Sleeps": 1,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:24:30",
        "Yawns": 2,
        "Sleeps": 1,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:25:00",
        "Yawns": 2,
        "Sleeps": 1,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:25:30",
        "Yawns": 2,
        "Sleeps": 1,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:26:00",
        "Yawns": 2,
        "Sleeps": 1,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:26:30",
        "Yawns": 2,
        "Sleeps": 1,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:27:00",
        "Yawns": 2,
        "Sleeps": 1,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:27:30",
        "Yawns": 2,
        "Sleeps": 1,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:28:00",
        "Yawns": 2,
        "Sleeps": 1,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:28:30",
        "Yawns": 2,
        "Sleeps": 2,
        "Yawns_increase": 0,
        "Sleeps_increase": 1
    },
    {
        "Date": "2023-01-10 08:29:00",
        "Yawns": 2,
        "Sleeps": 2,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:29:30",
        "Yawns": 2,
        "Sleeps": 2,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:30:00",
        "Yawns": 2,
        "Sleeps": 2,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:30:30",
        "Yawns": 2,
        "Sleeps": 3,
        "Yawns_increase": 0,
        "Sleeps_increase": 1
    },
    {
        "Date": "2023-01-10 08:31:00",
        "Yawns": 2,
        "Sleeps": 3,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:31:30",
        "Yawns": 2,
        "Sleeps": 3,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:32:00",
        "Yawns": 2,
        "Sleeps": 4,
        "Yawns_increase": 0,
        "Sleeps_increase": 1
    },
    {
        "Date": "2023-01-10 08:32:30",
        "Yawns": 2,
        "Sleeps": 4,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:33:00",
        "Yawns": 2,
        "Sleeps": 4,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:33:30",
        "Yawns": 2,
        "Sleeps": 4,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:34:00",
        "Yawns": 2,
        "Sleeps": 4,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:34:30",
        "Yawns": 2,
        "Sleeps": 4,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:35:00",
        "Yawns": 2,
        "Sleeps": 4,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:35:30",
        "Yawns": 2,
        "Sleeps": 4,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:36:00",
        "Yawns": 2,
        "Sleeps": 4,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:36:30",
        "Yawns": 2,
        "Sleeps": 4,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:37:00",
        "Yawns": 2,
        "Sleeps": 4,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:37:30",
        "Yawns": 2,
        "Sleeps": 4,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:38:00",
        "Yawns": 2,
        "Sleeps": 4,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:38:30",
        "Yawns": 2,
        "Sleeps": 4,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:39:00",
        "Yawns": 2,
        "Sleeps": 4,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:39:30",
        "Yawns": 2,
        "Sleeps": 4,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:40:00",
        "Yawns": 2,
        "Sleeps": 4,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:40:30",
        "Yawns": 2,
        "Sleeps": 4,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:41:00",
        "Yawns": 2,
        "Sleeps": 4,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:41:30",
        "Yawns": 2,
        "Sleeps": 4,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:42:00",
        "Yawns": 2,
        "Sleeps": 4,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:42:30",
        "Yawns": 2,
        "Sleeps": 4,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:43:00",
        "Yawns": 2,
        "Sleeps": 4,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:43:30",
        "Yawns": 2,
        "Sleeps": 4,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:44:00",
        "Yawns": 2,
        "Sleeps": 4,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:44:30",
        "Yawns": 2,
        "Sleeps": 4,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:45:00",
        "Yawns": 2,
        "Sleeps": 4,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:45:30",
        "Yawns": 2,
        "Sleeps": 4,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:46:00",
        "Yawns": 2,
        "Sleeps": 4,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:46:30",
        "Yawns": 2,
        "Sleeps": 4,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:47:00",
        "Yawns": 2,
        "Sleeps": 4,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:47:30",
        "Yawns": 2,
        "Sleeps": 4,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:48:00",
        "Yawns": 2,
        "Sleeps": 4,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:48:30",
        "Yawns": 2,
        "Sleeps": 4,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:49:00",
        "Yawns": 2,
        "Sleeps": 4,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:49:30",
        "Yawns": 2,
        "Sleeps": 4,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:50:00",
        "Yawns": 2,
        "Sleeps": 4,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:50:30",
        "Yawns": 2,
        "Sleeps": 4,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:51:00",
        "Yawns": 2,
        "Sleeps": 4,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:51:30",
        "Yawns": 2,
        "Sleeps": 4,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:52:00",
        "Yawns": 2,
        "Sleeps": 4,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:52:30",
        "Yawns": 2,
        "Sleeps": 4,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:53:00",
        "Yawns": 2,
        "Sleeps": 4,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:53:30",
        "Yawns": 2,
        "Sleeps": 4,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:54:00",
        "Yawns": 2,
        "Sleeps": 4,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:54:30",
        "Yawns": 2,
        "Sleeps": 4,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:55:00",
        "Yawns": 2,
        "Sleeps": 4,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:55:30",
        "Yawns": 2,
        "Sleeps": 4,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:56:00",
        "Yawns": 2,
        "Sleeps": 4,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:56:30",
        "Yawns": 2,
        "Sleeps": 4,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:57:00",
        "Yawns": 2,
        "Sleeps": 4,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:57:30",
        "Yawns": 3,
        "Sleeps": 4,
        "Yawns_increase": 1,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:58:00",
        "Yawns": 3,
        "Sleeps": 4,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:58:30",
        "Yawns": 3,
        "Sleeps": 4,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:59:00",
        "Yawns": 3,
        "Sleeps": 4,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 08:59:30",
        "Yawns": 3,
        "Sleeps": 4,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:00:00",
        "Yawns": 3,
        "Sleeps": 4,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:00:30",
        "Yawns": 3,
        "Sleeps": 4,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:01:00",
        "Yawns": 3,
        "Sleeps": 4,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:01:30",
        "Yawns": 3,
        "Sleeps": 4,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:02:00",
        "Yawns": 3,
        "Sleeps": 4,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:02:30",
        "Yawns": 3,
        "Sleeps": 4,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:03:00",
        "Yawns": 3,
        "Sleeps": 4,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:03:30",
        "Yawns": 4,
        "Sleeps": 4,
        "Yawns_increase": 1,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:04:00",
        "Yawns": 4,
        "Sleeps": 4,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:04:30",
        "Yawns": 4,
        "Sleeps": 4,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:05:00",
        "Yawns": 4,
        "Sleeps": 4,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:05:30",
        "Yawns": 4,
        "Sleeps": 4,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:06:00",
        "Yawns": 4,
        "Sleeps": 4,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:06:30",
        "Yawns": 4,
        "Sleeps": 4,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:07:00",
        "Yawns": 4,
        "Sleeps": 4,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:07:30",
        "Yawns": 5,
        "Sleeps": 4,
        "Yawns_increase": 1,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:08:00",
        "Yawns": 5,
        "Sleeps": 4,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:08:30",
        "Yawns": 5,
        "Sleeps": 4,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:09:00",
        "Yawns": 5,
        "Sleeps": 4,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:09:30",
        "Yawns": 5,
        "Sleeps": 4,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:10:00",
        "Yawns": 5,
        "Sleeps": 4,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:10:30",
        "Yawns": 5,
        "Sleeps": 4,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:11:00",
        "Yawns": 5,
        "Sleeps": 4,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:11:30",
        "Yawns": 5,
        "Sleeps": 4,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:12:00",
        "Yawns": 5,
        "Sleeps": 4,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:12:30",
        "Yawns": 5,
        "Sleeps": 4,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:13:00",
        "Yawns": 5,
        "Sleeps": 4,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:13:30",
        "Yawns": 5,
        "Sleeps": 4,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:14:00",
        "Yawns": 5,
        "Sleeps": 4,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:14:30",
        "Yawns": 5,
        "Sleeps": 4,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:15:00",
        "Yawns": 5,
        "Sleeps": 4,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:15:30",
        "Yawns": 5,
        "Sleeps": 4,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:16:00",
        "Yawns": 5,
        "Sleeps": 4,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:16:30",
        "Yawns": 6,
        "Sleeps": 4,
        "Yawns_increase": 1,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:17:00",
        "Yawns": 6,
        "Sleeps": 4,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:17:30",
        "Yawns": 6,
        "Sleeps": 4,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:18:00",
        "Yawns": 6,
        "Sleeps": 4,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:18:30",
        "Yawns": 6,
        "Sleeps": 4,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:19:00",
        "Yawns": 6,
        "Sleeps": 4,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:19:30",
        "Yawns": 6,
        "Sleeps": 4,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:20:00",
        "Yawns": 6,
        "Sleeps": 5,
        "Yawns_increase": 0,
        "Sleeps_increase": 1
    },
    {
        "Date": "2023-01-10 09:20:30",
        "Yawns": 6,
        "Sleeps": 5,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:21:00",
        "Yawns": 6,
        "Sleeps": 5,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:21:30",
        "Yawns": 6,
        "Sleeps": 5,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:22:00",
        "Yawns": 6,
        "Sleeps": 5,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:22:30",
        "Yawns": 6,
        "Sleeps": 5,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:23:00",
        "Yawns": 6,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 1
    },
    {
        "Date": "2023-01-10 09:23:30",
        "Yawns": 6,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:24:00",
        "Yawns": 6,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:24:30",
        "Yawns": 6,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:25:00",
        "Yawns": 6,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:25:30",
        "Yawns": 6,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:26:00",
        "Yawns": 6,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:26:30",
        "Yawns": 6,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:27:00",
        "Yawns": 6,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:27:30",
        "Yawns": 6,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:28:00",
        "Yawns": 6,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:28:30",
        "Yawns": 6,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:29:00",
        "Yawns": 6,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:29:30",
        "Yawns": 6,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:30:00",
        "Yawns": 6,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:30:30",
        "Yawns": 6,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:31:00",
        "Yawns": 6,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:31:30",
        "Yawns": 6,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:32:00",
        "Yawns": 6,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:32:30",
        "Yawns": 6,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:33:00",
        "Yawns": 6,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:33:30",
        "Yawns": 6,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:34:00",
        "Yawns": 6,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:34:30",
        "Yawns": 6,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:35:00",
        "Yawns": 6,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:35:30",
        "Yawns": 6,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:36:00",
        "Yawns": 6,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:36:30",
        "Yawns": 6,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:37:00",
        "Yawns": 6,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:37:30",
        "Yawns": 6,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:38:00",
        "Yawns": 6,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:38:30",
        "Yawns": 6,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:39:00",
        "Yawns": 6,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:39:30",
        "Yawns": 6,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:40:00",
        "Yawns": 6,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:40:30",
        "Yawns": 6,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:41:00",
        "Yawns": 6,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:41:30",
        "Yawns": 6,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:42:00",
        "Yawns": 6,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:42:30",
        "Yawns": 6,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:43:00",
        "Yawns": 6,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:43:30",
        "Yawns": 6,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:44:00",
        "Yawns": 6,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:44:30",
        "Yawns": 6,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:45:00",
        "Yawns": 6,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:45:30",
        "Yawns": 6,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:46:00",
        "Yawns": 6,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:46:30",
        "Yawns": 6,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:47:00",
        "Yawns": 6,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:47:30",
        "Yawns": 6,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:48:00",
        "Yawns": 6,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:48:30",
        "Yawns": 6,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:49:00",
        "Yawns": 6,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:49:30",
        "Yawns": 6,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:50:00",
        "Yawns": 6,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:50:30",
        "Yawns": 6,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:51:00",
        "Yawns": 6,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:51:30",
        "Yawns": 6,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:52:00",
        "Yawns": 6,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:52:30",
        "Yawns": 6,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:53:00",
        "Yawns": 6,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:53:30",
        "Yawns": 6,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:54:00",
        "Yawns": 6,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:54:30",
        "Yawns": 6,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:55:00",
        "Yawns": 6,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:55:30",
        "Yawns": 6,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:56:00",
        "Yawns": 6,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:56:30",
        "Yawns": 6,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:57:00",
        "Yawns": 6,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:57:30",
        "Yawns": 6,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:58:00",
        "Yawns": 6,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:58:30",
        "Yawns": 6,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:59:00",
        "Yawns": 6,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 09:59:30",
        "Yawns": 6,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:00:00",
        "Yawns": 6,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:00:30",
        "Yawns": 7,
        "Sleeps": 6,
        "Yawns_increase": 1,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:01:00",
        "Yawns": 7,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:01:30",
        "Yawns": 7,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:02:00",
        "Yawns": 7,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:02:30",
        "Yawns": 7,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:03:00",
        "Yawns": 7,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:03:30",
        "Yawns": 7,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:04:00",
        "Yawns": 7,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:04:30",
        "Yawns": 7,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:05:00",
        "Yawns": 7,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:05:30",
        "Yawns": 7,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:06:00",
        "Yawns": 7,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:06:30",
        "Yawns": 7,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:07:00",
        "Yawns": 7,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:07:30",
        "Yawns": 8,
        "Sleeps": 6,
        "Yawns_increase": 1,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:08:00",
        "Yawns": 8,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:08:30",
        "Yawns": 8,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:09:00",
        "Yawns": 8,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:09:30",
        "Yawns": 8,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:10:00",
        "Yawns": 8,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:10:30",
        "Yawns": 8,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:11:00",
        "Yawns": 8,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:11:30",
        "Yawns": 8,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:12:00",
        "Yawns": 8,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:12:30",
        "Yawns": 8,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:13:00",
        "Yawns": 8,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:13:30",
        "Yawns": 8,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:14:00",
        "Yawns": 8,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:14:30",
        "Yawns": 8,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:15:00",
        "Yawns": 8,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:15:30",
        "Yawns": 8,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:16:00",
        "Yawns": 8,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:16:30",
        "Yawns": 8,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:17:00",
        "Yawns": 8,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:17:30",
        "Yawns": 8,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:18:00",
        "Yawns": 8,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:18:30",
        "Yawns": 8,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:19:00",
        "Yawns": 8,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:19:30",
        "Yawns": 8,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:20:00",
        "Yawns": 8,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:20:30",
        "Yawns": 8,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:21:00",
        "Yawns": 8,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:21:30",
        "Yawns": 8,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:22:00",
        "Yawns": 8,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:22:30",
        "Yawns": 8,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:23:00",
        "Yawns": 8,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:23:30",
        "Yawns": 8,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:24:00",
        "Yawns": 8,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:24:30",
        "Yawns": 8,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:25:00",
        "Yawns": 8,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:25:30",
        "Yawns": 8,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:26:00",
        "Yawns": 8,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:26:30",
        "Yawns": 8,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:27:00",
        "Yawns": 8,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:27:30",
        "Yawns": 8,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:28:00",
        "Yawns": 8,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:28:30",
        "Yawns": 8,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:29:00",
        "Yawns": 8,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:29:30",
        "Yawns": 8,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:30:00",
        "Yawns": 8,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:30:30",
        "Yawns": 8,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:31:00",
        "Yawns": 8,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:31:30",
        "Yawns": 8,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:32:00",
        "Yawns": 8,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:32:30",
        "Yawns": 8,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:33:00",
        "Yawns": 8,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:33:30",
        "Yawns": 8,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:34:00",
        "Yawns": 8,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:34:30",
        "Yawns": 8,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:35:00",
        "Yawns": 8,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:35:30",
        "Yawns": 8,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:36:00",
        "Yawns": 8,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:36:30",
        "Yawns": 8,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:37:00",
        "Yawns": 8,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:37:30",
        "Yawns": 8,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:38:00",
        "Yawns": 8,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:38:30",
        "Yawns": 8,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:39:00",
        "Yawns": 8,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:39:30",
        "Yawns": 8,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:40:00",
        "Yawns": 8,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:40:30",
        "Yawns": 8,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:41:00",
        "Yawns": 8,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:41:30",
        "Yawns": 8,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:42:00",
        "Yawns": 8,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:42:30",
        "Yawns": 8,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:43:00",
        "Yawns": 8,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:43:30",
        "Yawns": 9,
        "Sleeps": 6,
        "Yawns_increase": 1,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:44:00",
        "Yawns": 9,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:44:30",
        "Yawns": 9,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:45:00",
        "Yawns": 9,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:45:30",
        "Yawns": 9,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:46:00",
        "Yawns": 9,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:46:30",
        "Yawns": 9,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:47:00",
        "Yawns": 9,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:47:30",
        "Yawns": 9,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:48:00",
        "Yawns": 9,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:48:30",
        "Yawns": 9,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:49:00",
        "Yawns": 9,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:49:30",
        "Yawns": 9,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:50:00",
        "Yawns": 9,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:50:30",
        "Yawns": 9,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:51:00",
        "Yawns": 9,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:51:30",
        "Yawns": 9,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:52:00",
        "Yawns": 9,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:52:30",
        "Yawns": 9,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:53:00",
        "Yawns": 9,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:53:30",
        "Yawns": 9,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:54:00",
        "Yawns": 9,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:54:30",
        "Yawns": 9,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:55:00",
        "Yawns": 9,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:55:30",
        "Yawns": 9,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:56:00",
        "Yawns": 9,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:56:30",
        "Yawns": 9,
        "Sleeps": 6,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:57:00",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 1
    },
    {
        "Date": "2023-01-10 10:57:30",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:58:00",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:58:30",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:59:00",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 10:59:30",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:00:00",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:00:30",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:01:00",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:01:30",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:02:00",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:02:30",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:03:00",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:03:30",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:04:00",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:04:30",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:05:00",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:05:30",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:06:00",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:06:30",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:07:00",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:07:30",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:08:00",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:08:30",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:09:00",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:09:30",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:10:00",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:10:30",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:11:00",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:11:30",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:12:00",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:12:30",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:13:00",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:13:30",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:14:00",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:14:30",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:15:00",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:15:30",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:16:00",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:16:30",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:17:00",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:17:30",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:18:00",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:18:30",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:19:00",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:19:30",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:20:00",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:20:30",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:21:00",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:21:30",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:22:00",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:22:30",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:23:00",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:23:30",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:24:00",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:24:30",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:25:00",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:25:30",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:26:00",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:26:30",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:27:00",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:27:30",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:28:00",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:28:30",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:29:00",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:29:30",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:30:00",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:30:30",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:31:00",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:31:30",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:32:00",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:32:30",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:33:00",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:33:30",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:34:00",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:34:30",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:35:00",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:35:30",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:36:00",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:36:30",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:37:00",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:37:30",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:38:00",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:38:30",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:39:00",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:39:30",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:40:00",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:40:30",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:41:00",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:41:30",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:42:00",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:42:30",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:43:00",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:43:30",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:44:00",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:44:30",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:45:00",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:45:30",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:46:00",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:46:30",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:47:00",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:47:30",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:48:00",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:48:30",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:49:00",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:49:30",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:50:00",
        "Yawns": 9,
        "Sleeps": 7,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:50:30",
        "Yawns": 9,
        "Sleeps": 8,
        "Yawns_increase": 0,
        "Sleeps_increase": 1
    },
    {
        "Date": "2023-01-10 11:51:00",
        "Yawns": 9,
        "Sleeps": 8,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:51:30",
        "Yawns": 9,
        "Sleeps": 8,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:52:00",
        "Yawns": 9,
        "Sleeps": 8,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:52:30",
        "Yawns": 9,
        "Sleeps": 8,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:53:00",
        "Yawns": 9,
        "Sleeps": 8,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:53:30",
        "Yawns": 9,
        "Sleeps": 8,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:54:00",
        "Yawns": 9,
        "Sleeps": 8,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:54:30",
        "Yawns": 9,
        "Sleeps": 8,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:55:00",
        "Yawns": 9,
        "Sleeps": 8,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:55:30",
        "Yawns": 9,
        "Sleeps": 8,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:56:00",
        "Yawns": 9,
        "Sleeps": 8,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:56:30",
        "Yawns": 9,
        "Sleeps": 8,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:57:00",
        "Yawns": 9,
        "Sleeps": 9,
        "Yawns_increase": 0,
        "Sleeps_increase": 1
    },
    {
        "Date": "2023-01-10 11:57:30",
        "Yawns": 9,
        "Sleeps": 9,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:58:00",
        "Yawns": 9,
        "Sleeps": 9,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:58:30",
        "Yawns": 9,
        "Sleeps": 9,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:59:00",
        "Yawns": 9,
        "Sleeps": 9,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 11:59:30",
        "Yawns": 9,
        "Sleeps": 9,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 12:00:00",
        "Yawns": 9,
        "Sleeps": 9,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 12:00:30",
        "Yawns": 9,
        "Sleeps": 9,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 12:01:00",
        "Yawns": 9,
        "Sleeps": 9,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 12:01:30",
        "Yawns": 9,
        "Sleeps": 9,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 12:02:00",
        "Yawns": 9,
        "Sleeps": 9,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 12:02:30",
        "Yawns": 9,
        "Sleeps": 9,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 12:03:00",
        "Yawns": 9,
        "Sleeps": 9,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 12:03:30",
        "Yawns": 9,
        "Sleeps": 9,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 12:04:00",
        "Yawns": 9,
        "Sleeps": 9,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 12:04:30",
        "Yawns": 9,
        "Sleeps": 10,
        "Yawns_increase": 0,
        "Sleeps_increase": 1
    },
    {
        "Date": "2023-01-10 12:05:00",
        "Yawns": 9,
        "Sleeps": 10,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 12:05:30",
        "Yawns": 9,
        "Sleeps": 10,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 12:06:00",
        "Yawns": 9,
        "Sleeps": 10,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 12:06:30",
        "Yawns": 9,
        "Sleeps": 10,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 12:07:00",
        "Yawns": 9,
        "Sleeps": 10,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 12:07:30",
        "Yawns": 9,
        "Sleeps": 10,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 12:08:00",
        "Yawns": 9,
        "Sleeps": 10,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 12:08:30",
        "Yawns": 9,
        "Sleeps": 10,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 12:09:00",
        "Yawns": 9,
        "Sleeps": 10,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 12:09:30",
        "Yawns": 9,
        "Sleeps": 10,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 12:10:00",
        "Yawns": 9,
        "Sleeps": 10,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 12:10:30",
        "Yawns": 9,
        "Sleeps": 10,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    },
    {
        "Date": "2023-01-10 12:11:00",
        "Yawns": 9,
        "Sleeps": 10,
        "Yawns_increase": 0,
        "Sleeps_increase": 0
    }
])
