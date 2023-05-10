import random
import numpy as np
import matplotlib.pyplot as plt
import holidays
from copy import copy
from datetime import datetime, timedelta
from fatigue_log import FatigueLog

# Matematyczna funkcja prawdopodobienstwa dla ziewania
def probability_distribution(x):
    return 0.088 * x ** 2 - 0.078 * x + 0.03


# Funkcja sprawdza czy data jest wolna od pracy w naszym pieknym kraju
def is_holiday_in_poland(date):
    return date in holidays.Poland()


# Funkcja generuje dane dla jednego dnia
def generate_one_day(start_hour=8, shift_duration=8, tick_interval=30):
    shift_tick_length = shift_duration * 60 * (
            60 / tick_interval)  # Zapisanie dlugosci zmiany w tickach na potrzeby generowania
    shift_tick_regular_finish_time = 8 * 60 * (
            60 / tick_interval)  # Czas zakonczenia normalnej zmiany (8 - 16) na potrzeby funkcji prawdopodobienstwa
    shift_tick_start = (start_hour - 8) * 60 * (60 / tick_interval)  # Startowy tick wzgledem normalnej zmiany
    shift_tick_end = shift_tick_start + shift_tick_length  # Koncowy tick
    ticks = []
    yawns = []
    sleeps = []
    acceptance_history = []  # Historia prawdopodobienstwa na rzecz wizualizacji
    current_tick = shift_tick_start
    # Glowna petla do generowania - szansa na wygenerowanie przy kazdym ticku zalezna od funkcji
    # probability_distribution
    while current_tick < shift_tick_end:
        acceptance_prob = probability_distribution(current_tick / shift_tick_regular_finish_time)  # Szansa w danym ticku
        acceptance_history.append(acceptance_prob)
        ticks.append(current_tick)
        # Losowanie czy w danym ticku bylo ziewane / spane
        if np.random.rand() < acceptance_prob:
            yawns.append(1)
        else:
            yawns.append(0)
        if np.random.rand() < acceptance_prob:
            sleeps.append(1)
        else:
            sleeps.append(0)
        current_tick += 1

    return ticks, yawns, sleeps
    # Plot the histogram of the accepted points
    # plt.plot(ticks, yawns)
    # plt.plot(ticks, sleeps)
    # plt.plot(ticks, acceptance_history)
    # plt.show()


# Funkcja konwertuje wygenerowane ticki z ziewnięciami w obiekt FatigueLog
def convert_day_ticks_to_FatigueLog(date, tick_array, yawns_array, sleeps_array, tick_interval=30):
    yawns = 0
    sleeps = 0

    def convert_tick_to_FatigueLog(tick, yawn, sleep):
        day_progress = tick / (8*60*(60/tick_interval))
        timestamp = copy(date)
        shift_hour = int((tick * tick_interval) / 60 // 60)
        timestamp = timestamp.replace(hour=8 + shift_hour)
        tick -= shift_hour * 60 * (60 / tick_interval)
        shift_minute = int((tick * tick_interval) // 60)
        timestamp = timestamp.replace(minute=shift_minute)
        tick -= shift_minute * (60 / tick_interval)
        shift_second = int(tick * tick_interval)
        timestamp = timestamp.replace(second=shift_second)
        return FatigueLog(timestamp, yawns, sleeps, int(yawn), int(sleep), day_progress)

    fatigue_logs = []
    for i in range(0, len(tick_array)):
        if yawns_array[i]:
            yawns += 1
        if sleeps_array[i]:
            sleeps += 1
        fatigue_logs.append(convert_tick_to_FatigueLog(tick_array[i], yawns_array[i], sleeps_array[i]))

    return fatigue_logs


# Funkcja generuje godziny w jakich odbywa sie praca, mozna sprecyzowac godziny pracy przez podanie argumentow
#   Domyslnie start_hour jest losowany z 7-10, shift_length losowany z 7-9
def generate_shift_times(start_hour=None, finish_hour=None, shift_length=None, possible_shift_lengths=None):
    if possible_shift_lengths is None:
        possible_shift_lengths = [7, 8, 9]
    if start_hour is None and finish_hour is None and shift_length is None:
        start_hour = random.choice([7, 8, 9, 10])
        shift_length = random.choice(possible_shift_lengths)
        finish_hour = start_hour + shift_length
    elif start_hour is None and finish_hour is None:
        start_hour = random.choice([7, 8, 9, 10])
        finish_hour = start_hour + shift_length
    elif start_hour is None and shift_length is None:
        shift_length = random.choice(possible_shift_lengths)
        start_hour = finish_hour - shift_length
    elif finish_hour is None and shift_length is None:
        shift_length = random.choice(possible_shift_lengths)
        finish_hour = start_hour + shift_length
    elif start_hour is None:
        start_hour = finish_hour - shift_length
    elif finish_hour is None:
        finish_hour = start_hour + shift_length
    elif shift_length is None:
        shift_length = finish_hour - start_hour

    if start_hour + shift_length != finish_hour:
        return AttributeError("Error: Times do not sum up")
    return [start_hour, finish_hour, shift_length]


# Glowna funkcja do generowania danych, przyjmuje date poczatkowa i koncowa, mozna ustalic konkretne godziny pracy,
#   oraz prace w dnie wolne, domyslnie wylaczone
def generate_in_date_range(start_date, end_date, skip_holidays=True, forced_start_hour=None,
                           forced_finish_hour=None, forced_shift_length=None, possible_shift_lengths=None):
    current_date = start_date
    all_logs = []
    while current_date < end_date:
        shift_hours = generate_shift_times(forced_start_hour, forced_finish_hour,
                                           forced_shift_length, possible_shift_lengths)

        ticks, yawns, sleeps = generate_one_day(shift_hours[0], shift_hours[2])
        day_FatigueLog = convert_day_ticks_to_FatigueLog(current_date, ticks, yawns, sleeps)
        all_logs.append(day_FatigueLog)
        current_date += timedelta(hours=24)
        if skip_holidays:
            while is_holiday_in_poland(current_date):
                current_date += timedelta(hours=24)

    write_to_file(all_logs)


# Zapis logow do pliku
def write_to_file(logs):
    with open('./mock_data.csv', 'w') as file:
        file.write('Date,Yawns,Sleeps,Yawns_increase,Sleeps_increase,Day_progress\n')
        for day in logs:
            for log in day:
                file.write(log.__str__() + '\n')


generate_in_date_range(datetime(2023, 1, 10), datetime(2023, 4, 20))