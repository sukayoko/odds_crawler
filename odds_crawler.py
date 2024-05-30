from const import *
import time, sys, os
import datetime as dt
import locale
import argparse
from const import *
from ipat_selenium_driver import IpatSeleniumDriver
from influxdb_client import InfluxDBClient, Point
from influxdb_local_client import InfluxDBLocalClient
from datetime import datetime, timezone, timedelta
from netkeiba_crawler import NetkeibaCrawler
from selenium.webdriver.common.by import By
from typing import List
from util import time_to_milliseconds
from nar_race_result_crawl import NarRaceResultCrawler
import re

# 
class OddsCrawler:
    


    def __init__(self, bucket):
        pass

    def __del__(self):
        pass

    def main(self, mode) :
        # 起動メッセージ
        print("起動しました")
        print(f"実行時間は土曜日、日曜日 {START_HOUR}:00～{END_HOUR}:00 の間です。")
        # 一定時間ごとに crawl
        self.main_loop(mode)

    def nar_odds_crawl_main(self, mode):
        # 起動メッセージ
        print("地方競馬オッズ収集プログラムを起動しました")
        print(f"実行時間は浦和競馬開催日 {NAR_START_HOUR}:00～{NAR_END_HOUR}:00 の間です。")
        # 一定時間ごとに crawl
        self.main_loop(mode)    

    # プログラム起動中ずっとこのループ処理をし続ける
    def main_loop(self,mode) :

        bef_exec_now = time.time() - (INTERVAL_MINUTES * 60 * 1000)
        # 指定した時間以外は休止
        ###  定期的に実行
        while True:
            
            now = datetime.now()
            day_of_week = now.weekday()
            current_hour = now.hour
            cur_exec_now = time.time()

            ## 中央版        
            # 曜日が 5, 6(土日)であれば
            if  mode == "jra-odds" and day_of_week >= 0 and (START_HOUR <= current_hour <= END_HOUR):
                # influxDB登録用クライアント
                influxClient =  InfluxDBLocalClient("jra_race_odds")
                # 前回実行時から一定間隔あいたら実行する(初回は即実行)
                if ( (cur_exec_now - bef_exec_now) > (INTERVAL_MINUTES * 60)):
                    bef_exec_now = cur_exec_now
                    # オッズを取得　して influxDBに登録
                    # driverを定期的に作り直さないとプロセスが残り続けてしまう？初期化処理

                    chromeDriver = IpatSeleniumDriver("temp")
                    chromeDriver.driver.get("https://www.jra.go.jp/keiba/")
                    # 登録用のPointリストをwebから取得
                    points_list = self.jra_odds_crawl(chromeDriver)

                    # ここで登録のほうがよさそう
                    # 3場分 * 12R分 * 単・複の2種類 で最大 72データ

                    if (len(points_list) > 0) :
                        influxClient.register_point_list(points_list)

                # 次の処理実行まで待機
                time.sleep(1)

            #### 地方版
            elif mode == "nar-odds" and (NAR_START_HOUR <= current_hour <= NAR_END_HOUR):
                # influxDB登録用クライアント
                influxClient =  InfluxDBLocalClient("nar_race_odds")
                # 前回実行時から一定間隔あいたら実行する(初回は即実行)
                if ( (cur_exec_now - bef_exec_now) > (INTERVAL_MINUTES * 60)):
                    bef_exec_now = cur_exec_now
                    # オッズを取得　して influxDBに登録
                    # driverを定期的に作り直さないとプロセスが残り続けてしまう？初期化処理

                    chromeDriver = IpatSeleniumDriver("temp")
                    chromeDriver.driver.get("https://www.keiba.go.jp/KeibaWeb/TodayRaceInfo/TodayRaceInfoTop")
                    # 登録用のPointリストをwebから取得
                    points_list = self.nar_odds_crawl(chromeDriver)

                    # ここで登録のほうがよさそう
                    # 1場分 * 12R分 * 単・複の2種類
                    if (len(points_list) > 0) :
                        influxClient.register_point_list(points_list)

                    # 時間かかるので明示的に呼び出し
                    chromeDriver.__del__()

                # 次の処理実行まで待機
                time.sleep(1)            

            # 時間外になったら待機
            else:
                time.sleep(INTERVAL_MINUTES * 60)

        ### while メインループここまで

    def jra_odds_crawl(chromeDriver : IpatSeleniumDriver) :
        ### 現時点では当日の A, B, C 場のオッズのみを取得する

        chromeDriver.click_element_by_a_text("オッズ")

        # 今週のオッズ配下に開催一覧がある
        kaisai_elem = chromeDriver.get_element_by_class(chromeDriver.driver, "thisweek")
        panel_elems = chromeDriver.get_elements_by_class(kaisai_elem, "panel")

        # 今週のオッズが未発表だと Noneになるはず
        if (panel_elems != None) :
            # 巡回リストを作成 Ex. ['5回中山7日', '5回阪神7日', '5回中山8日', '5回阪神8日', '5回中山9日', '5回阪神9日']
            crawl_ba_list = []
            # influx登録用 Pointリスト
            point_list : Point = []

            panel_idx = 0
            # 開催日毎、場毎にページがある
            for p_elem in panel_elems :
                title_elem = chromeDriver.get_element_by_class(p_elem, "sub_header")
                # print(title_elem.text)

                # 当日でない場合はスキップする          
                match_date = re.match(r"(\d+)月(\d+)日", title_elem.text)
                # if True:
                # # TODO
                if match_date:

                    month = int(match_date.group(1))
                    day = int(match_date.group(2))

                    current_date = datetime.now()
                    # TODO
                    if month == current_date.month and day == current_date.day :
                    # if month == 1 and day == 6 :
                        for ba_elem in chromeDriver.get_ba_list_from_atag(p_elem) :
                            crawl_ba_list.append(ba_elem)
                    
                        break
                
                else:
                    # TODO 例外
                    print("正規表現が一致しませんでした。")
                    sys.exit()

                panel_idx = panel_idx + 1
                
            if len(crawl_ba_list) > 0 :
                # ここで一回画面遷移しないとエラーになってしまう。。
                chromeDriver.click_element_by_a_text(crawl_ba_list[0])
                # print(crawl_ba_list)

            # A, B, C 場毎に処理
            for ba_i in range(len(crawl_ba_list)):
                # 順番にオッズページを確認
                # 開催場名の一覧を取り直してクリック
                # 二日目、三日目の取得
                ul_elem = chromeDriver.get_element_by_class(chromeDriver.driver, "data_list_unit", panel_idx)
                ba_elem_list = chromeDriver.get_ba_list_from_oddspage(ul_elem)
                ba_elem_list[ba_i].click()

                tanpuku_elem = chromeDriver.get_element_by_class(chromeDriver.driver, "tanpuku")
                tanpuku_elem.click()     

                # Error発生
                #tanpuku_elem.click()
                #AttributeError: 'NoneType' object has no attribute 'click'

                # 次のレース
                race_num_list = chromeDriver.get_race_list_from_page()
                # print("場:" + str(ba_i))
                for i in range(len(race_num_list)):
                    # print("R:" + str(i+1))
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

                    # ジョッキー名も取る

                    # 数字の文字列ではないものは 0.0 に変換
                    for k in range(len(result)):
                        try:
                            float(result[k])
                        except ValueError:
                            result[k] = "0.0"
                    # print(",".join(result))
                    
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
                    
                    # 一つのレース、馬番順に単勝オッズをリストに追加
                    for uma_no in range(len(result)):
                        point_list.append( 
                            Point(race_place_id)
                            .tag(RACE_NO, i+1)
                            .tag(TAG_BETTING_TYPE, "単勝")
                            .tag(TAG_COMBINE, uma_no+1)
                            .field("odds", float(result[uma_no]))
                        )

                    ### 複勝へ移動
                    # テーブルから取得
                    result_fuku = chromeDriver.get_fuku_odds_list_from_table(chromeDriver.driver, "odds_fuku")
                    # 先頭の要素を取り除く
                    result_fuku = result_fuku[1:]
                    # 数字の文字列ではないものは 0.0 に変換
                    for k in range(len(result_fuku)):
                        try:
                            float(result_fuku[k])
                        except ValueError:
                            result_fuku[k] = "0.0"
                    # print(",".join(result_fuku))

                    # 一つのレース、馬番順に単勝オッズをリストに追加
                    for uma_no in range(len(result)):
                        point_list.append( 
                            Point(race_place_id)
                            .tag(RACE_NO, i+1)
                            .tag(TAG_BETTING_TYPE, "複勝")
                            .tag(TAG_COMBINE, uma_no+1)
                            .field("odds", float(result_fuku[uma_no]))
                        )

                    # 1R分完成

                
                # 12R分完成？
                # ここで登録するとどうなる
                        
                # CHECK TODO もしオッズがまだない状態だとどうなる？？

        return point_list

    #######################
    def nar_odds_crawl(chromeDriver : IpatSeleniumDriver) :
        # influx登録用 Pointリスト
        point_list : Point = []
        ### 現時点では当日の 浦和競馬のオッズのみを取得する
        babaName = "浦和"

        # 本日配下の競馬場を取得する
        # 存在しなかったらクリックしない
        if (chromeDriver.click_today_ba_list_from_nar(babaName)):
            # おそらく1Rのオッズに遷移するはず..
            chromeDriver.click_element_by_a_text("オッズ")

            # https://www.keiba.go.jp/KeibaWeb/TodayRaceInfo/RaceList?k_raceDate=2024%2f01%2f04&k_babaCode=21
            cur_url = chromeDriver.driver.current_url

            # https://www.keiba.go.jp/KeibaWeb/TodayRaceInfo/OddsTanFuku?k_raceDate=2024%2f01%2f04&k_raceNo=1&k_babaCode=21
            # オッズのページに遷移したい
            # オッズを取得 # 存在しないページの場合は オッズが取得できない
            for raceno in range(1,12+1):
                odds_url = cur_url.replace("RaceList", "OddsTanFuku")
                odds_url = odds_url.replace("k_raceNo=1", "k_raceNo=" + str(raceno))
                chromeDriver.driver.get(odds_url)
                # time.sleep(1)

                odds_table_elem = chromeDriver.get_element_by_class(chromeDriver.driver, "odd_popular_table_02")
                if (odds_table_elem != None):
                    tr_list = chromeDriver.get_elements_by_tag(odds_table_elem, "tr")
                    for tr in tr_list:
                        col_list = tr.find_elements(By.TAG_NAME, "td")

                        if len(col_list) > 9:
                            # print(col_list[1].text) # 馬番
                            # print(col_list[2].text) # 馬名
                            # print(col_list[3].text) # 単勝オッズ
                            # print(col_list[4].text) # 複勝  1.0-
                            # print(col_list[9].text) # ジョッキー

                            jokey_name = str(col_list[9].text).replace("★","").replace("▲","").replace("△","").replace("◇","").replace("☆","")
                            modified_jokey_name = re.sub(r'\（[^)]*\）', '', jokey_name)

                            # print(modified_jokey_name)
                            # print(col_list[3].text)
                            # print(str(col_list[4].text).replace("-", ""))

                            # オッズが数字に変換出来ない場合は 0.0とする
                            try:
                                tan_odds = float(col_list[3].text.strip())
                            except ValueError:
                                tan_odds = 0.0

                            # 単勝
                            point_list.append( 
                                Point(babaName)
                                .tag(RACE_NO, raceno)
                                .tag(TAG_BETTING_TYPE, "単勝")
                                .tag(TAG_COMBINE, col_list[1].text)
                                .tag(JOKEY_NAME, modified_jokey_name)
                                .field("odds", tan_odds)
                            )

                            # オッズが数字に変換出来ない場合は 0.0とする
                            try:
                                fuku_odds = float(str(col_list[4].text).replace("-", "").strip())
                            except ValueError:
                                fuku_odds = 0.0

                            # 複勝 オッズの末尾 - は取り除く
                            point_list.append( 
                                Point(babaName)
                                .tag(RACE_NO, raceno)
                                .tag(TAG_BETTING_TYPE, "複勝")
                                .tag(TAG_COMBINE, col_list[1].text)
                                .tag(JOKEY_NAME, modified_jokey_name)
                                .field("odds", fuku_odds)
                            )
        return point_list


        