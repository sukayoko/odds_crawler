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
from util import time_to_milliseconds

# 地方競馬のレース結果登録用クラス
class NarRaceResultCrawler :

    # コンストラクタ
    # ba_name: "浦和" とか "大井"
    def __init__(self, file_path, ba_name, dev_flag:bool):
        self.chromeDriver = IpatSeleniumDriver(file_path)
        self.baName = ba_name
        self.devFlag = dev_flag

    def __del__(self):
        pass
    
    # postgresDB登録用クライアント

    def nar_race_result_crawl_main(self):

        # babaCode :
        # 浦和 18
        # 大井 20
        # current_url = "https://www.keiba.go.jp/KeibaWeb/TodayRaceInfo/RaceList?k_raceDate=2024%2f05%2f16&k_babaCode=18"
        current_url = "https://www.keiba.go.jp/KeibaWeb/TodayRaceInfo/RaceList?k_raceDate=2024%2f05%2f16&k_babaCode=20"
        self.chromeDriver.driver.get(current_url)

        finish_flag = False
        
        # 翌日がなくなるまでループ
        while True:
            # print(current_url)
            self.chromeDriver.driver.get(current_url)
            tomorrow_elem = self.chromeDriver.get_element_by_class(self.chromeDriver.driver, "tomorrow")
            if(tomorrow_elem == None):
                finish_flag = True
            else :
                next_url = tomorrow_elem.get_attribute("href")
        
            # 成績リストを取得して番号
            # a_tag_list = chromeDriver.get_elements_by_tag_and_text(chromeDriver.driver, "a", "成績")
            a_tag_list = self.chromeDriver.get_elements_by_tag_and_text_except_class(self.chromeDriver.driver, "a", "成績", "disable")
            cur_url = self.chromeDriver.driver.current_url

            # 途中から開始した場合はエラーになりそう
            for race_no in range(len(a_tag_list)):  
                raceResult_list_by_race: List[NarRaceResultObj] = []

                result_url = cur_url.replace("RaceList", "RaceMarkTable")
                result_url = result_url + "&k_raceNo=" + str(race_no+1)
                self.chromeDriver.driver.get(result_url)

                # 次の日
                # date_elem = chromeDriver.get_element_by_class("current")

                # テーブルのリストをとる
                # 一つ目　メニュー
                # 二つ目　レース情報
                # 三つ目　賞金
                # ４つ目　成績表
                # 5つめ　成績表
                # 6つめ　コーナー通過順
                # 
                table_bs_list = self.chromeDriver.get_elements_by_class(self.chromeDriver.driver, "bs")
                if table_bs_list != None and len(table_bs_list) < 4 : 
                    print("error")
                    sys.exit()

                # レース情報
                race_info_elem = self.chromeDriver.get_element_by_tag_and_contain_text(table_bs_list[1], "td", "")
                # print(race_info_elem.text)

                date_pattern = re.compile(r'(\d{4})年(\d{1,2})月(\d{1,2})日')
                distance_pattern = r'(\d+)ｍ'  # 数字（1回以上） + "ｍ"
                weather_pattern = r'天候：([^\s]+)'  # "天候：" + 空白以外の文字（1回以上）
                ground_condition_pattern = r'馬場：([^\s]+)'  # "馬場：" + 空白以外の文字（1回以上）                

                date_match = date_pattern.search(race_info_elem.text)
                distance_match = re.search(distance_pattern, race_info_elem.text)
                weather_match = re.search(weather_pattern, race_info_elem.text)
                ground_condition_match = re.search(ground_condition_pattern, race_info_elem.text)

                
                race_info_elems = self.chromeDriver.get_elements_by_class(self.chromeDriver.driver, "midium")
                # rule_pettern = re.compile(r'サラブレッド系([^\s]+)')  # "サラブレッド系" + 空白以外の文字（1回以上）
                rule_pettern = re.compile(r'サラブレッド系　([^\s]+)')  # "サラブレッド系" + 空白以外の文字（1回以上）
                # rule_pettern_match = re.search(rule_pettern, race_info_elems[0].text)
                rule_pettern_match = rule_pettern.search(race_info_elems[0].text)

                # print(f"{date_match.group(1)}, {date_match.group(2)}, {date_match.group(3)}")
                # print(f"{rule_pettern_match.group(1)}")

                # 結果を表示
                if date_match :
                    date = date_match.group(0)
                if distance_match:
                    distance = distance_match.group(1)
                if weather_match:
                    weather = weather_match.group(1)
                if ground_condition_match:
                    ground_condition = ground_condition_match.group(1) 
                if rule_pettern_match:
                    rule = rule_pettern_match.group(1)

                # コーナ通過順
                # [['1,3,7,2,5,10,11,4,9,6,8'], ['1,3,7,10,2,5,11,4,6,9,8'], ['3,1,10,7,2,11,6,5,9,4,8'], ['3,2,11,7,10,1,6,9,4,5,8']]
                corner_elem = self.chromeDriver.get_element_by_tag_and_contain_text(table_bs_list[5], "td", "コーナー通過順")
                if (corner_elem != None):
                    
                    # 不要文字列置換
                    modified_corner_text = corner_elem.text.replace("-",",").replace("=",",").replace("(","").replace(")","")
                    # 改行毎
                    lines_list = modified_corner_text.split('\n')
                    # 1行目削除
                    # 先頭の *角 を削除
                    cleansing_line = []
                    for line in lines_list[1:]:
                        cleansing_line.append(line.split(" ")[1:])

                    # print(cleansing_line)
                # なかった場合
                else:
                    print("corner not exist.")

                # 成績　dbtbl は 4つある　そのうちのひとつ目
                result_table_elem = self.chromeDriver.get_element_by_class(self.chromeDriver.driver, "dbtbl", 0)
                if (result_table_elem != None):
                    tr_list = self.chromeDriver.get_elements_by_tag(result_table_elem, "tr")
                    if len(tr_list) < 4:
                        print("error")
                        sys.exit()

                    # trの1行目、2行目はヘッダなので飛ばす
                    for tr in tr_list[2:]:
                        col_list = tr.find_elements(By.TAG_NAME, "td")

                        if len(col_list) > 14:
                            # 着順がない行はスキップ(取り消しのはず)
                            uma_result_data = NarRaceResultObj()
                            try:
                                int(col_list[0].text)
                            except ValueError:
                                continue

                            uma_result_data.date = datetime( int(date_match.group(1)), int(date_match.group(2)), int(date_match.group(3)), int(race_no+1), 0, 0)
                            # timescale用に日付のフォーマットが必要？
                            uma_result_data.ba = self.baName
                            uma_result_data.race_num = race_no+1
                            uma_result_data.distance = distance
                            uma_result_data.weather = weather
                            uma_result_data.ground_condition = ground_condition
                            uma_result_data.rule = rule

                            uma_result_data.horse_name = col_list[3].text
                            uma_result_data.position = int(col_list[0].text)
                            uma_result_data.umaban = int(col_list[2].text)
                            uma_result_data.age = int(col_list[5].text.split(" ")[1])
                            uma_result_data.sex = col_list[5].text.split(" ")[0]

                            uma_result_data.affiliation = col_list[4].text

                            try :
                                float(col_list[6].text)
                                uma_result_data.additional_weight = float(col_list[6].text)
                            except ValueError:
                                uma_result_data.additional_weight = 0        

                            jokey_name = str(col_list[7].text).replace("★","").replace("▲","").replace("△","").replace("◇","").replace("☆","")
                            modified_jokey_name = re.sub(r'\([^)]*\)', '', jokey_name)

                            uma_result_data.jokey_name = modified_jokey_name
                            uma_result_data.trainer_name = col_list[8].text

                            try :
                                float(col_list[9].text)
                                uma_result_data.weight = float(col_list[9].text)
                            except ValueError:
                                uma_result_data.weight = 0

                            # 体重を丸める
                            uma_result_data.rounded_weight = round(uma_result_data.weight / 5) * 5

                            uma_result_data.record = time_to_milliseconds(col_list[11].text)  # タイム 1:38.5　〇
                            uma_result_data.popularity = int(col_list[14].text)

                            uma_result_data.last_three_furlong = float(col_list[13].text)

                            rate = 0
                            for n_corner in cleansing_line:
                                try:
                                    pos = str(uma_result_data.umaban)
                                    c_pos = n_corner[0].split(",").index( pos )
                                except ValueError:
                                    print("list error")
                                    sys.exit()

                                rate = rate + c_pos + 1
                                
                            # 補正をかける
                            if len(cleansing_line) < 4 :
                                if len(cleansing_line) == 1:
                                    rate = rate * 4
                                elif len(cleansing_line) == 2:
                                    rate = rate * 2
                                elif len(cleansing_line) == 3:
                                    rate = (rate / 3) * 4

                            uma_result_data.corner_position_rate = rate
                            # 登録リストに追加
                            raceResult_list_by_race.append(uma_result_data)

                    # 父、父父、母父の情報をとりにいく
                    tr_list = self.chromeDriver.get_elements_by_tag(result_table_elem, "tr")
                    if len(tr_list) < 3:
                        print("error")
                        sys.exit()

                    # trの1行目、2行目はヘッダなので飛ばす
                    u_index = 2
                    current_result_url = self.chromeDriver.driver.current_url
                    while True:

                        # 元の画面に戻る
                        self.chromeDriver.driver.get(current_result_url)
                        result_table_elem = self.chromeDriver.get_element_by_class(self.chromeDriver.driver, "dbtbl", 0)
                        new_tr_list = self.chromeDriver.get_elements_by_tag(result_table_elem, "tr")
                        
                        # trの1行目、2行目はヘッダなので飛ばす
                        if (u_index >= len(new_tr_list)):
                            break
                        col_list = new_tr_list[u_index].find_elements(By.TAG_NAME, "td")
                        # 着順がない行はスキップ(取り消しのはず)
                        try:
                            int(col_list[0].text)
                        except ValueError:
                            u_index = u_index + 1
                            continue

                        # 馬のリンクを取得
                        # https://www.keiba.go.jp/KeibaWeb/DataRoom/RaceHorseInfo?k_lineageLoginCode=30034402066&k_activeCode=1
                        #    &k_activeCode=1
                        # https://www.keiba.go.jp/KeibaWeb/DataRoom/HorseMarkInfo?k_lineageLoginCode=30043407876&k_activeCode=2
                        a_tag_uma_list = self.chromeDriver.get_elements_by_tag(col_list[3], "a")
                        a_elem = a_tag_uma_list[0]
                        uma_url = a_elem.get_attribute("href")
                        # 出走履歴画面へ遷移
                        self.chromeDriver.driver.get(uma_url)
                        horse_mark_info_table_elem = self.chromeDriver.get_element_by_class(self.chromeDriver.driver, "HorseMarkInfo_table", 0)
                        if (horse_mark_info_table_elem != None):
                            horse_mark_info_list = self.chromeDriver.get_elements_by_tag(horse_mark_info_table_elem, "tr")
                            # 出走履歴が一つもない場合は 999週間隔とする(デフォルト値)
                            if len(horse_mark_info_list) < 3:
                                pass
                            else:
                                # trの1行目、2行目はヘッダなので飛ばす
                                for horse_mark_info_tr in horse_mark_info_list[2:]:
                                    col_list = horse_mark_info_tr.find_elements(By.TAG_NAME, "td")
                                    #出走年月日
                                    pre_race_date_pattern = re.compile(r'(\d{4})/(\d{1,2})/(\d{1,2})')
                                    
                                    pre_race_date_match = pre_race_date_pattern.search(col_list[0].text)
                                    pre_race_datetime = datetime( int(pre_race_date_match.group(1)), int(pre_race_date_match.group(2)), int(pre_race_date_match.group(3)), int(race_no+1), 0, 0)
                                    diff_day = raceResult_list_by_race[u_index-2].date - pre_race_datetime

                                    raceResult_list_by_race[u_index-2].pre_race_interval_week = int(diff_day.days / 7)

                                    break

                        # 出走履歴画面のURLを馬情報画面のURLへ変更
                        uma_url = uma_url.replace("HorseMarkInfo","RaceHorseInfo") + "&k_activeCode=1"
                        self.chromeDriver.driver.get(uma_url)

                        # 生年月日、馬主、牧場を取得
                        horse_info_table_elem = self.chromeDriver.get_element_by_class(self.chromeDriver.driver, "horse_info_table", 0)
                        if (horse_info_table_elem != None):
                            horse_info_list = self.chromeDriver.get_elements_by_tag(horse_info_table_elem, "tr")
                            if len(horse_info_list) < 4:
                                print("error")
                                sys.exit()

                            # trの1行目、2行目はヘッダなので飛ばす
                            p_index = 1
                            for horse_info_tr in horse_info_list[1:]:
                                col_list = horse_info_tr.find_elements(By.TAG_NAME, "td")
                                if p_index == 1:
                                    # 1行目
                                    # 2019.03.14生 なので変換が必要
                                    bd_str = col_list[1].text[:-1]
                                    date_obj = datetime.strptime(bd_str, '%Y.%m.%d').date()
                                    # 年は一律1900年に変更
                                    raceResult_list_by_race[u_index-2].birthday = date_obj.replace(year=1900)
                                elif p_index == 2:
                                    # 2行目の3
                                    raceResult_list_by_race[u_index-2].owner_name = col_list[3].text
                                elif p_index == 3:
                                    # 三行目の3
                                    raceResult_list_by_race[u_index-2].farm = col_list[3].text
                                p_index = p_index+1

                        pedigree_table_elem = self.chromeDriver.get_element_by_class(self.chromeDriver.driver, "pedigree", 0)
                        if (pedigree_table_elem != None):
                            pedigree_tr_list = self.chromeDriver.get_elements_by_tag(pedigree_table_elem, "tr")
                            if len(pedigree_tr_list) < 5:
                                print("error")
                                sys.exit()

                            # trの1行目、2行目はヘッダなので飛ばす
                            p_index = 1
                            for pedigree_tr in pedigree_tr_list[1:]:
                                col_list = pedigree_tr.find_elements(By.TAG_NAME, "td")
                                if p_index == 1:
                                    # 一行目
                                    raceResult_list_by_race[u_index-2].f_name = col_list[1].text
                                    # 1行目の3
                                    raceResult_list_by_race[u_index-2].ff_name = col_list[3].text
                                elif p_index == 3:
                                    # 三行目の3
                                    raceResult_list_by_race[u_index-2].mf_name = col_list[3].text
                                p_index = p_index+1

                        u_index = u_index + 1
                    ##### while loop

                    # for race_row in raceResult_list_by_race:
                    #     print(race_row)

                    # 1レース分ずつ登録していく
                    # 一つのレース、馬番順に単勝オッズをリストに追加 #TODO
                    local_time = datetime( int(date_match.group(1)), int(date_match.group(2)), int(date_match.group(3)), 0, 0, 0)

                    psql_client = PostgresClient()
                    psql_client.register_nar_race_result(raceResult_list_by_race)

            # 翌日のデータがないなら終了        
            if(finish_flag) :
                break

            current_url = next_url