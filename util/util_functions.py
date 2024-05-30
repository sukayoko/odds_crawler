# util/util_functions.py

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