import time, sys, os
import argparse
from const import *
from local_config import LocalConfig
from ipat_selenium_driver import IpatSeleniumDriver
from datetime import datetime, timedelta


def main() :
    # ここから
    RACE_INFO_URL = (
        "https://www.keiba.go.jp/KeibaWeb_IPAT/TodayRaceInfo/TodayRaceInfoTop_ipat"
    )

    # プログラムの実行時間範囲と実行間隔
    START_HOUR = 9
    END_HOUR = 22
    
    INTERVAL_MINUTES = 1

    init_flag = True

    # 起動メッセージ
    print("地方レース情報通知ツールを起動しました。")
    print(f"実行時間は毎日 {START_HOUR}:00～{END_HOUR+1}:00 の間です。")

    # 9:00～22:59 以外は休止
    ###  定期的に実行
    while True:
        # driverを定期的に作り直さないとプロセスが残り続けてしまう？初期化処理
        chromeDriver = IpatSeleniumDriver(resource_path("temp"))
        now = datetime.now()
        current_hour = now.hour
        current_minute = now.minute
        
        if START_HOUR <= current_hour <= END_HOUR:
            if current_hour == START_HOUR and current_minute < INTERVAL_MINUTES:
                # 処理を開始するために少し待機
                time.sleep((INTERVAL_MINUTES - current_minute) * 60)

            # 当日初回実行の場合は tempディレクトリは以下を削除する。
            if init_flag:
                initialize()

                # とりあえず 名古屋 11R
                # ファイル作成


                init_flag = False

            # オッズを取得してファイルを更新
            # 本日のレース情報を取得して tempファイルに保存する
            chromeDriver.get_race_info(RACE_INFO_URL)

            # 次の処理実行まで待機
            time.sleep(INTERVAL_MINUTES * 60)

        # 時間外になったら初期化フラグオフ
        else:
            init_flag = True
            time.sleep(INTERVAL_MINUTES * 60)

        # driverを定期的に作り直さないとプロセスが残り続けてしまう？終了処理
        # chromeDriver.end()
    ### while メインループここまで


def resource_path(relative_path):
    # TODO exe化する時と開発するときでパスが変わる
    try:
        base_path = sys._MEIPASS
        # exe化用（ダブルクリックで実行したとき、実行ファイルの配置場所のパスとなる）
        # base_path = os.getcwd()
    except Exception:
        base_path = os.path.dirname(__file__)
    return os.path.join(base_path, relative_path)

def initialize():
    temp_path = resource_path("temp")
    # TODO ディレクトリがないときエラーになる
    for filename in os.listdir(temp_path):
        file_path = os.path.join(temp_path, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)
            print(f"ファイル {filename} を削除しました")

def remove_old_file(directory_path):
    target_string = "old"  # 削除したい特定の文字列

    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        if os.path.isfile(file_path) and target_string in filename:
            os.remove(file_path)
            # print(f"ファイルを削除しました: {filename}")

# main
if __name__ == "__main__":

    # オプションの設定
    parser = argparse.ArgumentParser(description='oddsの取得')
    # テストか開催か mode の設定
    # TODO: 設定を初期化するinit があってもいい？
    parser.add_argument('-m', '--mode', choices=['test', 'normal'], default='test', help='Specify a mode test or normal. default test.')
    # 中央か地方か locale の設定
    parser.add_argument('-l', '--locale', choices=['center', 'national'], default='center', help='Specify a locale center or national. default center.')
    # 国際含むかどうか
    # TODO
    # 実施パターン 複数指定可能
    parser.add_argument('-p', '--pattern', nargs='+', choices=['all', 'galaho', 'limit', 'umaca'], default='all', help='choise')
    args = parser.parse_args()

    print(f"Selected mode: {args.mode}")
    print(f"Selected locale: {args.locale}")
    print(f"Selected pattern: {args.pattern}")

    main()


