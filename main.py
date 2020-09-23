# -*- coding: utf-8 -*-
import csv
from collections import defaultdict
from datetime import datetime
import calendar
from typing import Dict, List

"""
T = температура повітря
Ff = швидкість вітру
RRR = кількість випавших осадків
"""


def read_csv(path):
    """ Read csv file """
    rows = []
    with open(path, encoding="utf-8", errors='ignore', newline='') as file:
        reader = csv.DictReader(file, delimiter=';')
        columns = ['city_time', 'T', 'Ff', 'RRR']
        for row in reader:
            rows.append(dict([(col, row.get(col)) for col in columns]))
    return rows


def format_data(data):
    for row in data:
        row['city_time'] = datetime.strptime(row['city_time'], '%d.%m.%Y %H:%M')
        row['T'] = float(row['T'])
        row['Ff'] = float(row['Ff'])
        try:
            row['RRR'] = float(row['RRR'])
        except ValueError:
            row['RRR'] = 0.0


def year_exist(e: Dict, row: Dict):
    """ Checking year in dict
    :return: {"2016": defaultdict(int)} or {"2016": {1:0, 2:1, ..., 12:0}}
    """
    try:
        year = e[str(row['city_time'].year)]
    except KeyError:
        year = defaultdict(int)
    return year


def format_float(param):
    return round(param, 2)


def count_days_in_month(row):
    """
    :return: Портає кількість днів в місяці
    """
    return calendar.monthrange(row['city_time'].year, row['city_time'].month)[1]


def calculate_wind_on_month(data: List[Dict]):
    """
    Обчислення середньої швидкості вітру на місяць
    :param data: list({}, {})
    """
    e = {}
    for row in data:
        year = year_exist(e, row)
        # Визначаємо кількість днів в місяці
        days_in_month = count_days_in_month(row)
        # Вираховуємо середнє значення швидкості вітру на місяць
        year[row['city_time'].month] += row['Ff'] / days_in_month
        # Зберігаємо дані за місяць до відповідного року
        e[str(row['city_time'].year)] = year

    for year, item in e.items():
        # Визначаємо максимальну середню швидківсть вітру в місяць за відповідний рік
        max_wind_month = max(item.items(), key=lambda x: x[1])
        print(f"In {year} year a max average wind speed on "
              f"{calendar.month_name[max_wind_month[0]]} is {format_float(max_wind_month[1])} m/s")


def calculate_temperature_of_month(data: List[Dict]):
    """
    Обчислення середньої температури повітря на місяць
    :param data: list({}, {})
    """
    e = {}
    for row in data:
        year = year_exist(e, row)
        # Визначаємо кількість днів в місяці
        days_in_month = count_days_in_month(row)
        # Вираховуємо середню температуру на місяць
        year[row['city_time'].month] += row['T'] / days_in_month
        # Зберігаємо дані за місяць до відповідного року
        e[str(row['city_time'].year)] = year

    for year, item in e.items():
        # Визначаємо мінімальну середню температуру повітря в місяць
        min_temp_on_month = min(item.items(), key=lambda x: x[1])
        print(f"In {year} year a min average temperature on "
              f"{calendar.month_name[min_temp_on_month[0]]} is {format_float(min_temp_on_month[1])}")
        # Визначаємо максимальну середню температуру повітря в місяць
        max_temp_on_month = max(item.items(), key=lambda x: x[1])
        print(f"In {year} year a max average temperature on "
              f"{calendar.month_name[max_temp_on_month[0]]} is {format_float(max_temp_on_month[1])}")


def calculate_precipitation(data: List[Dict]):
    """
    Обчислення максимальної кількості опадів на тиждень
    """
    e = {}
    c = calendar.Calendar(firstweekday=0)
    for row in data:
        days_in_week = {}

        try:
            year = e[row['city_time'].year]
        except KeyError:
            year = {}

        weeks = defaultdict(int)
        # Складання маски по тижнях в місяць
        for week_number, week in enumerate(c.monthdays2calendar(row['city_time'].year, row['city_time'].month)):
            weeks[week_number] += 0
            for day, day_of_week in week:
                days_in_week[day] = week_number

        try:
            year[row['city_time'].month]
        except KeyError:
            year[row['city_time'].month] = weeks
        # Обчислення кількості опадів на тиждень
        year[row['city_time'].month][days_in_week[row['city_time'].day]] += row['RRR']
        # Збереження даних за місяць до відповідного року
        e[row['city_time'].year] = year

    max_precipitation_on_years = []
    for y, yd in e.items():
        for m, mw in yd.items():
            # Визначаємо максимальні опади в місяці за тиждень
            max_precipitation_on_years.append((y, m, max(mw.items(), key=lambda x: x[1])))

    # Отримуємо максимальні опади на тиждень за весь період
    # (рік, місяць, (номер тижня, кількість опадів))
    m = max(max_precipitation_on_years, key=lambda x: x[2][1])
    for n, week in enumerate(c.monthdays2calendar(m[0], m[1])):
        # Визначаємо відповідність тижнів та отрмуємо діапазон дат в тижні з максимальними опадами
        if n == m[2][0]:
            print(f'Max precipitation on week '
                  f'{datetime(m[0], m[1], week[0][0]).date()} - {datetime(m[0], m[1], week[-1][0]).date()}: '
                  f'{format_float(m[2][1])}mm')


def run():
    data = read_csv('data.csv')
    format_data(data)
    # 1
    calculate_wind_on_month(data)
    # 2, 4
    calculate_temperature_of_month(data)
    # 3
    min_temp_on_day = min(data, key=lambda x: x['T'])
    print(f'Min temperature on day {min_temp_on_day["city_time"]} temp: {min_temp_on_day["T"]}')
    # 5
    max_temp_on_day = max(data, key=lambda x: x["T"])
    print(f'Max temperature on day {max_temp_on_day["city_time"]} temp: {max_temp_on_day["T"]}')
    # 6
    calculate_precipitation(data)


if __name__ == '__main__':
    run()
