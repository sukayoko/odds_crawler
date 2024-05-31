# util/util_functions.py
from datetime import datetime

def time_to_milliseconds(time_str):
    # 分と秒を取得
    minutes, seconds = map(float, time_str.split(':'))
    # 分をミリ秒に変換
    minutes_in_milliseconds = int(minutes * 60 * 1000)
    # 秒をミリ秒に変換
    seconds_in_milliseconds = int(seconds * 1000)
    # 合算してミリ秒に変換
    total_milliseconds = minutes_in_milliseconds + seconds_in_milliseconds

    return total_milliseconds

def get_nar_ba_code(ba_name) :
    ba_code = 0
    if (ba_name == "浦和"):
        ba_code = 18
    elif (ba_name == "大井"):
        ba_code = 20

    return ba_code

def get_year_month_day(date_str) :
    date_object = datetime.strptime(date_str, "%Y-%m-%d")

    year = date_object.year
    month = date_object.month
    day = date_object.day

    date_array = [year, month, day]
    return date_array