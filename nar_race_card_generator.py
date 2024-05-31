from const import *
from ipat_selenium_driver import IpatSeleniumDriver
from selenium.webdriver.common.by import By
from typing import List
import re
import time, sys
from datetime import datetime, timezone, timedelta
import datetime as dt
from race_result_obj import NarRaceResultObj
from psql import PostgresClient
from util import *

# 地方競馬の出馬表作成クラス
class NarRaceCardGenerator :

    # コンストラクタ
    def __init__(self, file_path, dev_flag:bool):
        self.chromeDriver = IpatSeleniumDriver(file_path)
        self.devFlag = dev_flag

    def __del__(self):
        pass

    # date_str : 2024-05-12
    # ba_name: "浦和" とか "大井"
    def nar_race_card_generate_main(self, date_str, ba_name):

        # 引数から年月日を取得
        date_arr = get_year_month_day(date_str)
        # 引数から場コードを取得
        ba_code = get_nar_ba_code(ba_name)

        # 当日のレース一覧画面へ
        current_url = "https://www.keiba.go.jp/KeibaWeb/TodayRaceInfo/RaceList?k_raceDate=" + str(date_arr[0]) + "%2f" + '{:02d}'.format(date_arr[1]) + "%2f" + '{:02d}'.format(date_arr[2]) + "&k_babaCode=" + str(ba_code)
        print(current_url)
        self.chromeDriver.driver.get(current_url)

        # レース数を取得
        # 開催がない場合は終了
        a_tag_list = self.chromeDriver.get_elements_by_tag_and_text_except_class(self.chromeDriver.driver, "a", "成績", "disable")
        if(a_tag_list == None):
            return

        for race_no in range(len(a_tag_list)):  

            # TODO
            # race_card_list_by_race: List[NarRaceResultObj] = []
            # 出馬表
            # https://www.keiba.go.jp/KeibaWeb/TodayRaceInfo/DebaTable?k_raceDate=2024%2f05%2f31&k_raceNo=1&k_babaCode=19
            current_url = "https://www.keiba.go.jp/KeibaWeb/TodayRaceInfo/DebaTable?k_raceDate=" + str(date_arr[0]) + "%2f" + '{:02d}'.format(date_arr[1]) + "%2f" + '{:02d}'.format(date_arr[2]) + "&k_raceNo=" + str(race_no+1) + "&k_babaCode=" + str(ba_code)
            self.chromeDriver.driver.get(current_url)
        
            # レース情報を取得
            # テーブルのリストをとる
            table_raceTitle_elem = self.chromeDriver.get_element_by_class(self.chromeDriver.driver, "raceTitle")
            if table_raceTitle_elem == None: 
                print("error")
                sys.exit()

            # レース情報
            race_info_elem = self.chromeDriver.get_elements_by_tag(table_raceTitle_elem, "li")
            # ダート　1600ｍ（内コース・右）　　天候：晴　　馬場：重　　サラブレッド系　一般 別定　　＊電話投票コード：33#
            race_info_text = race_info_elem[0].text
            print(race_info_text)

            distance_pattern = r'(\d+)ｍ'  # 数字（1回以上） + "ｍ"
            weather_pattern = r'天候：([^\s]+)'  # "天候：" + 空白以外の文字（1回以上）
            ground_condition_pattern = r'馬場：([^\s]+)'  # "馬場：" + 空白以外の文字（1回以上）                

            distance_match = re.search(distance_pattern, race_info_text)
            weather_match = re.search(weather_pattern, race_info_text)
            ground_condition_match = re.search(ground_condition_pattern, race_info_text)

            rule_pettern = re.compile(r'サラブレッド系　([^\s]+)')  # "サラブレッド系" + 空白以外の文字（1回以上）
            # rule_pettern_match = re.search(rule_pettern, race_info_elems[0].text)
            rule_pettern_match = rule_pettern.search(race_info_text)

            # 結果を表示
            if distance_match:
                distance = distance_match.group(1)
            if weather_match:
                weather = weather_match.group(1)
            if ground_condition_match:
                ground_condition = ground_condition_match.group(1) 
            if rule_pettern_match:
                rule = rule_pettern_match.group(1)

            print(distance)
            print(weather)
            print(ground_condition)                
            print(rule)

            # 馬ごとの処理
            card_table_elem = self.chromeDriver.get_element_by_class(self.chromeDriver.driver, "cardTable")
            if (card_table_elem != None):
                    horse_tr_list = self.chromeDriver.get_elements_by_tag(card_table_elem, "tr")
                    # trの1行目、2行目はヘッダなので飛ばす
                    h_index = 0

                    print(len(horse_tr_list))
                    for tr in horse_tr_list[2:]:                        
                        # 一頭ごとに trが11つ
                        # とりあえず tdを取得する
                        col_list = tr.find_elements(By.TAG_NAME, "td")

                        # 各馬1行目
                        if  (h_index % 11 == 0):
                            # 要素を作成                         
                            # for col in col_list:
                            #     print(col.text)

                            # # # 馬番
                            print(col_list[1].text)
                            # # # 馬名
                            print(col_list[2].text)
                            # # # 騎手名 (所属)
                            print(col_list[3].text)
                            pass
                            
                        # 各馬2行目
                        elif  (h_index % 11 == 7):
                            # for col in col_list:
                            #     print(col.text)                            
                            # 性別　年齢
                            print(col_list[0].text)
                            # # 誕生日 04.24生
                            print(col_list[2].text)
                            # # 負担重量 56.0　0-0-1-0
                            print(col_list[3].text)
                            pass
                        # 各馬3行目 
                        elif  (h_index % 11 == 8):                           
                            # for col in col_list:
                            #     print(col.text)
                            # 調教師 (所属)
                            print(col_list[1].text)
                            pass
                        # 各馬4行目
                        elif  (h_index % 11 == 9):                           
                            # for col in col_list:
                            #     print(col.text)
                            # 馬主
                            print(col_list[1].text)
                            pass
                        # 各馬5行目
                        elif  (h_index % 11 == 10):                           
                            # for col in col_list:
                            #     print(col.text)
                            # 生産牧場
                            print(col_list[1].text)

                            

                            pass

                    # 馬リストからもう一度ループ
                    # 馬毎の持ちタイム比較みたいなものができれば

                    # 馬名から残りの情報と指数を持ってくる
                    # 平均順位、母数　平均コーナ位置、母数
                    # 父と母父と父父

                    # 騎手名から

                    # 調教師から

                    # 馬主

                    # 生産牧場

                            

                        h_index = h_index + 1





            