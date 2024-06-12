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
from csv_writer import *


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
        # a_tag_list = self.chromeDriver.get_elements_by_tag_and_text_except_class(self.chromeDriver.driver, "a", "成績", "disable")
        a_tag_list = self.chromeDriver.get_elements_by_tag_and_text(self.chromeDriver.driver, "a", "成績")
        if(a_tag_list == None):
            return

        for race_no in range(len(a_tag_list)):
            # if(race_no == 2):
            #     break
            # 馬情報の一覧リスト
            raceCard_horse_list: List[NarRaceResultObj] = []

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
            # print(weather)
            # print(ground_condition)                
            print(rule)

            # 馬ごとの処理
            card_table_elem = self.chromeDriver.get_element_by_class(self.chromeDriver.driver, "cardTable")
            if (card_table_elem != None):
                    horse_tr_list = self.chromeDriver.get_elements_by_tag(card_table_elem, "tr")
                    # trの1行目、2行目はヘッダなので飛ばす
                    h_index = 0                    

                    # print(len(horse_tr_list))
                    for tr in horse_tr_list[2:]:

                        # 一頭ごとに trが11つ
                        # とりあえず tdを取得する
                        col_list = tr.find_elements(By.TAG_NAME, "td")

                        # 各馬1行目
                        if  (h_index % 11 == 0):
                            horseobj = NarRaceResultObj()
                            # 要素を作成                         
                            # for col in col_list:
                            #     print(col.text)

                            # # # 馬番
                            # 同枠の二頭目は colの位置がずれる!
                            pad = -1
                            # print(col_list[1].text)
                            if( str(col_list[1].text).isdigit()):
                                pad = 0

                            horseobj.umaban = int(col_list[1+pad].text)
                            # # # 馬名
                            horseobj.horse_name = col_list[2+pad].text
                            # # # 騎手名 (所属)
                            pattern = r"^(.*?)（.*?）$"
                            match = re.match(pattern, col_list[3+pad].text)
                            if match:
                                horseobj.jokey_name = match.group(1)
                            else :
                                horseobj.jokey_name = ""


                            pass
                            
                        # 各馬2行目
                        elif  (h_index % 11 == 7):
                            # for col in col_list:
                            #     print(col.text)                            
                            # 性別　年齢
                            match = re.match(r"([^\d]+)(\d+)", col_list[0].text)

                            horseobj.sex = match.group(1)
                            horseobj.age = int(match.group(2))
                            # # 誕生日 04.24生
                            bd_str = col_list[2].text[:-1]
                            date_obj = datetime.strptime(bd_str, '%m.%d').date()
                            horseobj.birthday = date_obj.replace(year=2000)
                            # # 負担重量 56.0　0-0-1-0
                            ## TODO 加工
                            horseobj.additional_weight = col_list[3].text
                            pass
                        # 各馬3行目 
                        elif  (h_index % 11 == 8):                           
                            # for col in col_list:
                            #     print(col.text)
                            
                            horseobj.f_name = col_list[0].text
                            # 調教師 (所属)
                            pattern = r"^(.*?)（.*?）$"
                            match = re.match(pattern,col_list[1].text)
                            if match:
                                horseobj.trainer_name = match.group(1)
                            else :
                                horseobj.trainer_name = ""
                            pass
                        # 各馬4行目
                        elif  (h_index % 11 == 9):                           
                            # for col in col_list:
                            #     print(col.text)
                            # 馬主
                            horseobj.owner_name = col_list[1].text
                            pass
                        # 各馬5行目
                        elif  (h_index % 11 == 10):                           
                            # for col in col_list:
                            #     print(col.text)
                            # （母父）
                            # 生産牧場
                            horseobj.mf_name = col_list[0].text.replace('（', '').replace('）', '')
                            horseobj.farm = col_list[1].text

                            raceCard_horse_list.append(horseobj)
                            pass

                        
                        h_index = h_index + 1

                    # csvに出力する準備
                    csv_writer = CsvWriter(str(race_no+1) + "R")
                    for horse in raceCard_horse_list:
                        csv_writer.write_row(horse.horse_name)
   
                    ground_condition = "重"

                    # 馬リストからもう一度ループ
                    # 馬毎の持ちタイム比較みたいなものができれば
                    for horse in raceCard_horse_list:
                        #### 平均順位、母数　平均コーナ位置、母数

                        positionRate = RaceStatObj()
                        cornerRate = RaceStatObj()
                        furlongRate = RaceStatObj()

                        rateArrays = [positionRate,cornerRate,furlongRate]

                        # 距離、条件、馬場状態と検索条件を引数にする

                        psql_client = PostgresClient()

                        for stat_i in range(12):
                            # 性別: 0
                            if stat_i == 0:
                                for race_state_obj in rateArrays :
                                    race_state_obj.sex_idx = 0.0
                                    race_state_obj.sex_total = 0
                                result = psql_client.get_sex_stats(ba_name, distance, ground_condition, rule, horse.sex)
                                if(result):
                                    res_i = 0
                                    for race_state_obj in rateArrays :
                                        race_state_obj.sex_idx = result[0][res_i]
                                        race_state_obj.sex_total = result[0][res_i+1]
                                        res_i = res_i+2
                                

                            # 年齢 : 1
                            if stat_i == 1:
                                for race_state_obj in rateArrays :
                                    race_state_obj.age_idx = 0.0
                                    race_state_obj.age_total = 0
                                result = psql_client.get_age_stats(ba_name, distance, ground_condition, rule, horse.age)
                                if(result):
                                    res_i = 0
                                    for race_state_obj in rateArrays :
                                        race_state_obj.age_idx = result[0][res_i]
                                        race_state_obj.age_total = result[0][res_i+1]
                                        res_i = res_i+2

                            # 生年月日 : 2
                            # skip
                            if stat_i == 2:
                                for race_state_obj in rateArrays :
                                    race_state_obj.birth_idx = 0.0
                                    race_state_obj.birth_total = 0
                            # 馬主 : 3
                            if stat_i == 3:
                                for race_state_obj in rateArrays :
                                    race_state_obj.owner_idx = 0.0
                                    race_state_obj.owner_total = 0
                                result = psql_client.get_owner_name_stats(ba_name, distance, ground_condition, rule, horse.owner_name)
                                if(result):
                                    res_i = 0
                                    for race_state_obj in rateArrays :
                                        race_state_obj.owner_idx = result[0][res_i]
                                        race_state_obj.owner_total = result[0][res_i+1]
                                        res_i = res_i+2
                            # 生産牧場 : 4
                            if stat_i == 4:
                                for race_state_obj in rateArrays :
                                    race_state_obj.farm_idx = 0.0
                                    race_state_obj.farm_total = 0
                                result = psql_client.get_farm_stats(ba_name, distance, ground_condition, rule, horse.farm)
                                if(result):
                                    res_i = 0
                                    for race_state_obj in rateArrays :
                                        race_state_obj.farm_idx = result[0][res_i]
                                        race_state_obj.farm_total = result[0][res_i+1]
                                        res_i = res_i+2
                            # 体重 : 5
                            # skip
                            if stat_i == 5:
                                for race_state_obj in rateArrays :
                                    race_state_obj.weight_idx = 0.0
                                    race_state_obj.weight_total = 0
                            # 騎手名 : 6
                            if stat_i == 6:
                                for race_state_obj in rateArrays :
                                    race_state_obj.jokey_idx = 0.0
                                    race_state_obj.jokey_total = 0                                
                                result = psql_client.get_jockey_stats(ba_name, distance, ground_condition, rule, horse.jokey_name)
                                print(horse.jokey_name)
                                if(result):
                                    res_i = 0
                                    for race_state_obj in rateArrays :
                                        race_state_obj.jokey_idx = result[0][res_i]
                                        race_state_obj.jokey_total = result[0][res_i+1]
                                        res_i = res_i+2
                                
                            # 調教師 : 7
                            if stat_i == 7:
                                for race_state_obj in rateArrays :
                                    race_state_obj.trainer_idx = 0.0
                                    race_state_obj.trainer_total = 0
                                result = psql_client.get_trainer_name_stats(ba_name, distance, ground_condition, rule, horse.trainer_name)
                                print(horse.trainer_name)
                                if(result):
                                    res_i = 0
                                    for race_state_obj in rateArrays :
                                        race_state_obj.trainer_idx = result[0][res_i]
                                        race_state_obj.trainer_total = result[0][res_i+1]
                                        res_i = res_i+2                                
                            # 父 : 8
                            if stat_i == 8:
                                for race_state_obj in rateArrays :
                                    race_state_obj.f_idx = 0.0
                                    race_state_obj.f_total = 0
                                result = psql_client.get_f_name_stats(ba_name, distance, ground_condition, rule, horse.f_name)
                                if(result):
                                    res_i = 0
                                    for race_state_obj in rateArrays :
                                        race_state_obj.f_idx = result[0][res_i]
                                        race_state_obj.f_total = result[0][res_i+1]
                                        res_i = res_i+2  
                            # 父父 : 9
                            # skip
                            if stat_i == 9:
                                for race_state_obj in rateArrays :
                                    race_state_obj.ff_idx = 0.0
                                    race_state_obj.ff_total = 0
                            # 母父 : 10
                            if stat_i == 10:
                                for race_state_obj in rateArrays :
                                    race_state_obj.mf_idx = 0.0
                                    race_state_obj.mf_total = 0
                                result = psql_client.get_mf_name_stats(ba_name, distance, ground_condition, rule, horse.mf_name)
                                if(result):
                                    res_i = 0
                                    for race_state_obj in rateArrays :
                                        race_state_obj.mf_idx = result[0][res_i]
                                        race_state_obj.mf_total = result[0][res_i+1]
                                        res_i = res_i+2 
                            # 前走間隔 : 11
                            if stat_i == 11:
                                for race_state_obj in rateArrays :
                                    race_state_obj.pre_race_idx = 0.0
                                    race_state_obj.pre_race_total = 0
                                result = psql_client.get_pre_race_interval_week_stats(ba_name, distance, ground_condition, rule, horse.pre_race_interval_week)
                                if(result):
                                    res_i = 0
                                    for race_state_obj in rateArrays :
                                        race_state_obj.pre_race_idx = result[0][res_i]
                                        race_state_obj.pre_race_total = result[0][res_i+1]
                                        res_i = res_i+2 

                        # 1行目組み立て
                        # csvに出力
                        csv_row = str(rateArrays[0].sex_idx) + "\t" + str(rateArrays[0].sex_total) + "\t" +\
                            str(rateArrays[0].age_idx) + "\t" + str(rateArrays[0].age_total) + "\t" +\
                            str(rateArrays[0].birth_idx) + "\t" + str(rateArrays[0].birth_total) + "\t" +\
                            str(rateArrays[0].owner_idx) + "\t" + str(rateArrays[0].owner_total) + "\t" +\
                            str(rateArrays[0].farm_idx) + "\t" + str(rateArrays[0].farm_total) + "\t" +\
                            str(rateArrays[0].weight_idx) + "\t" + str(rateArrays[0].weight_total) + "\t\t" +\
                            str(rateArrays[1].sex_idx) + "\t" + str(rateArrays[1].sex_total) + "\t" +\
                            str(rateArrays[1].age_idx) + "\t" + str(rateArrays[1].age_total) + "\t" +\
                            str(rateArrays[1].birth_idx) + "\t" + str(rateArrays[1].birth_total) + "\t" +\
                            str(rateArrays[1].owner_idx) + "\t" + str(rateArrays[1].owner_total) + "\t" +\
                            str(rateArrays[1].farm_idx) + "\t" + str(rateArrays[1].farm_total) + "\t" +\
                            str(rateArrays[1].weight_idx) + "\t" + str(rateArrays[1].weight_total) + "\t\t" +\
                            str(rateArrays[2].sex_idx) + "\t" + str(rateArrays[2].sex_total) + "\t" +\
                            str(rateArrays[2].age_idx) + "\t" + str(rateArrays[2].age_total) + "\t" +\
                            str(rateArrays[2].birth_idx) + "\t" + str(rateArrays[2].birth_total) + "\t" +\
                            str(rateArrays[2].owner_idx) + "\t" + str(rateArrays[2].owner_total) + "\t" +\
                            str(rateArrays[2].farm_idx) + "\t" + str(rateArrays[2].farm_total) + "\t" +\
                            str(rateArrays[2].weight_idx) + "\t" + str(rateArrays[2].weight_total) + "\t\t"
                        
                        csv_writer.write_row(csv_row)

                        # 2行目組み立て
                        csv_row = str(rateArrays[0].jokey_idx) + "\t" + str(rateArrays[0].jokey_total) + "\t" +\
                            str(rateArrays[0].trainer_idx) + "\t" + str(rateArrays[0].trainer_total) + "\t" +\
                            str(rateArrays[0].f_idx) + "\t" + str(rateArrays[0].f_total) + "\t" +\
                            str(rateArrays[0].ff_idx) + "\t" + str(rateArrays[0].ff_total) + "\t" +\
                            str(rateArrays[0].mf_idx) + "\t" + str(rateArrays[0].mf_total) + "\t" +\
                            str(rateArrays[0].pre_race_idx) + "\t" + str(rateArrays[1].pre_race_total) + "\t\t" +\
                            str(rateArrays[1].jokey_idx) + "\t" + str(rateArrays[1].jokey_total) + "\t" +\
                            str(rateArrays[1].trainer_idx) + "\t" + str(rateArrays[1].trainer_total) + "\t" +\
                            str(rateArrays[1].f_idx) + "\t" + str(rateArrays[1].f_total) + "\t" +\
                            str(rateArrays[1].ff_idx) + "\t" + str(rateArrays[1].ff_total) + "\t" +\
                            str(rateArrays[1].mf_idx) + "\t" + str(rateArrays[1].mf_total) + "\t" +\
                            str(rateArrays[1].pre_race_idx) + "\t" + str(rateArrays[1].pre_race_total) + "\t\t" +\
                            str(rateArrays[2].jokey_idx) + "\t" + str(rateArrays[2].jokey_total) + "\t" +\
                            str(rateArrays[2].trainer_idx) + "\t" + str(rateArrays[2].trainer_total) + "\t" +\
                            str(rateArrays[2].f_idx) + "\t" + str(rateArrays[2].f_total) + "\t" +\
                            str(rateArrays[2].ff_idx) + "\t" + str(rateArrays[2].ff_total) + "\t" +\
                            str(rateArrays[2].mf_idx) + "\t" + str(rateArrays[2].mf_total) + "\t" +\
                            str(rateArrays[2].pre_race_idx) + "\t" + str(rateArrays[2].pre_race_total) + "\t\t"                                          
                        # csvに出力
                        csv_writer.write_row(csv_row)                       
                        pass

                    
                    

                            






            