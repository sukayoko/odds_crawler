import time, sys, os
import datetime as dt
import locale
import argparse
from const import *
from local_config import LocalConfig
from ipat_selenium_driver import IpatSeleniumDriver
from datetime import datetime, timedelta
from selenium.webdriver.common.by import By
import re


def main() :
    # 一定時間ごとに crawl ?
    main_loop()



def jra_odds_crawl() :
    ### 現時点では当日の A, B, C 場のオッズのみを取得する
    chromeDriver = IpatSeleniumDriver(resource_path("temp"))
    chromeDriver.driver.get("https://www.jra.go.jp/keiba/")

    chromeDriver.click_element_by_a_text("オッズ")

    # 今週のオッズ配下に開催一覧がある
    kaisai_elem = chromeDriver.get_element_by_class(chromeDriver.driver, "thisweek")
    if (kaisai_elem != None) :
        panel_elems = chromeDriver.get_elements_by_class(kaisai_elem, "panel")

        # 巡回リストを作成 Ex. ['5回中山7日', '5回阪神7日', '5回中山8日', '5回阪神8日', '5回中山9日', '5回阪神9日']
        crawl_ba_list = []

        # 開催日毎、場毎にページがある
        for p_elem in panel_elems :
            title_elem = chromeDriver.get_element_by_class(p_elem, "sub_header")
            print(title_elem.text)

            # 当日でない場合はスキップする          
            match_date = re.match(r"(\d+)月(\d+)日", title_elem.text)
            if match_date:
                month = int(match_date.group(1))
                day = int(match_date.group(2))

                current_date = datetime.now()
                # TODO
                # if month == current_date.month and day == current_date.day :
                if month == 12 and day == 24 :
                    for ba_elem in chromeDriver.get_ba_list_from_atag(p_elem) :
                        crawl_ba_list.append(ba_elem)
            
            else:
                # TODO 例外
                print("正規表現が一致しませんでした。")
                sys.exit()
            
        if len(crawl_ba_list) > 0 :
            # ここで一回画面遷移しないとエラーになってしまう。。
            chromeDriver.click_element_by_a_text(crawl_ba_list[0])
            print(crawl_ba_list)

        for ba_i in range(len(crawl_ba_list)):
            # 順番にオッズページを確認
            # 開催場名の一覧を取り直してクリック
            ul_elem = chromeDriver.get_element_by_class(chromeDriver.driver, "data_line_list")
            ba_elem_list = chromeDriver.get_ba_list_from_oddspage(ul_elem)
            ba_elem_list[ba_i].click()

            tanpuku_elem = chromeDriver.get_element_by_class(chromeDriver.driver, "tanpuku")
            # TODO もし存在すれば
            tanpuku_elem.click()     

            # 次のレース
            race_num_list = chromeDriver.get_race_list_from_page()
            print("場:" + str(ba_i))
            for i in range(len(race_num_list)):
                print("R:" + str(i+1))
                # 毎回取得しなおす
                race_num_list = chromeDriver.get_race_list_from_page()
                # race_num_list[i].click()
                chromeDriver.driver.execute_script("arguments[0].click()", race_num_list[i])
                ### 先頭にヘッダも入る "単勝"
                ### TODO 取り消しの場合　"取消"　が入るはず　
                # 1レース目だけ行けたらOK 次のページでオッズ、場の一覧が見れるので
                ### オッズ一覧のページ
                # 単勝オッズ取る この処理は早すぎるとダメっぽい
                # time.sleep(1)

                 # テーブルから取得
                result = chromeDriver.get_odds_list_from_table(chromeDriver.driver, "odds_tan")
                # 先頭の要素を取り除く
                result = result[1:]

                # 数字の文字列ではないものは 0.0 に変換
                for k in range(len(result)):
                    try:
                        float(result[k])
                    except ValueError:
                        result[k] = "0.0"
                print(",".join(result))
                
                race_place_id = "N"
                if ba_i == 0 :
                    race_place_id = "A"
                    pass
                elif ba_i == 1 :
                    race_place_id = "B"
                    pass
                elif ba_i == 2 :
                    race_place_id = "C"
                    pass
                else :
                    pass

                # register_odds(race_place_id, race_number, betting_type, combine, odds)
                    # race_number i+1
                    # BETTING_TYPE_TANSYO

                ### ワイドへ移動
                # chromeDriver.click_element_by_a_text("ワイド")



            
            # CHECK TODO もしオッズがまだない状態だとどうなる？？

    # driverを定期的に作り直さないとプロセスが残り続けてしまう？終了処理
    chromeDriver.end()

def main_loop() :

    init_flag = True
    
    # 起動メッセージ
    print("起動しました")
    print(f"実行時間は土曜日、日曜日 {START_HOUR}:00～{END_HOUR}:00 の間です。")

    locale.setlocale(locale.LC_TIME, "ja_JP.UTF-8")
    bef_exec_now = time.time() - (INTERVAL_MINUTES * 60 * 1000)
    # 指定した時間以外は休止
    ###  定期的に実行
    while True:
        
        now = datetime.now()
        day_of_week = now.weekday()
        current_hour = now.hour
        current_minute = now.minute
        cur_exec_now = time.time()
        
        # 曜日が 5, 6(土日)であれば
        if  day_of_week >= 5 and (START_HOUR <= current_hour <= END_HOUR):
            # 当日初回実行の場合は tempディレクトリは以下を削除する。
            if init_flag:
                # initialize()
                init_flag = False

            # 前回実行時から一定間隔あいたら実行する
            if ( (cur_exec_now - bef_exec_now) > (INTERVAL_MINUTES * 60)):
                bef_exec_now = cur_exec_now
                # オッズを取得
                # driverを定期的に作り直さないとプロセスが残り続けてしまう？初期化処理
                jra_odds_crawl()

            # 次の処理実行まで待機
            time.sleep(1)

        # 時間外になったら初期化フラグオフ
        else:
            init_flag = True
            time.sleep(INTERVAL_MINUTES * 60)



        # break
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

    main()


