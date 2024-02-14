import time, sys, os
import datetime as dt
import locale
import argparse
from const import *
from ipat_selenium_driver import IpatSeleniumDriver
from influxdb_client import InfluxDBClient, Point
from influxdb_local_client import InfluxDBLocalClient
from datetime import datetime, timezone, timedelta
from selenium.webdriver.common.by import By
from typing import List
import re

def resource_path(relative_path):
    # TODO exe化する時と開発するときでパスが変わる
    try:
        base_path = sys._MEIPASS
        # exe化用（ダブルクリックで実行したとき、実行ファイルの配置場所のパスとなる）
        # base_path = os.getcwd()
    except Exception:
        base_path = os.path.dirname(__file__)
    return os.path.join(base_path, relative_path)

# ジョッキー一覧を取得
def jra_jokey_crawl():
    chromeDriver = IpatSeleniumDriver(resource_path("temp"))
    chromeDriver.driver.get("https://www.jra.go.jp/datafile/leading/")

    chromeDriver.click_element_by_a_text("騎手")
    # ul_elem = chromeDriver.get_element_by_class(chromeDriver.driver, "data_line_list")

    while True :
        j_list = chromeDriver.get_jokeis_list_from_table(chromeDriver.driver, "name")

        for j_name in j_list:
            print(j_name)

        if (chromeDriver.click_element_by_a_text("次の20件")) :
            time.sleep(1)
        else :
            break    


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


#######################
def nar_race_result_crawl() :

    chromeDriver = IpatSeleniumDriver(resource_path("temp"))
    
    ### 現時点では当日の 浦和競馬のオッズのみを取得する
    babaName = "浦和"
    # influxDB登録用クライアント
    # influxClient =  InfluxDBLocalClient("nar_race_result")
    influxClient =  InfluxDBLocalClient("nar_race_result")

    # 構造体
    class umaResult:
        distance: int
        weather: str
        ground_condition: str
        position: int   #着順
        umaban: int     #馬番
        horse_name: str
        affiliation: str # 所属
        age : int # 年齢
        sex : str # 性別
        additional_weight : float # 負担重量
        jokey_name : str
        trainer_name : str
        weight : float # バ体重
        record : int # 走破時間 (ミリ秒に変換)
        popularity : int # 人気度
        corner_position_rate : int # それぞれのコーナでの位置の合計　低いほど前目にいたということ
        f_name: str #父親の名前
        mf_name: str # 母父の名前

        def __str__(self):
            return f"{self.distance}, {self.weather}, {self.ground_condition}, {self.position}, {self.umaban}, {self.horse_name}, {self.affiliation}, {self.age}, {self.sex}, {self.additional_weight},{self.jokey_name}, {self.trainer_name}, {self.weight}, {self.record}, {self.popularity}, {self.corner_position_rate}, {self.f_name}, {self.mf_name}"


    # current_url = "https://www.keiba.go.jp/KeibaWeb/TodayRaceInfo/RaceList?k_raceDate=2023%2f01%2f10&k_babaCode=18"
    current_url = "https://www.keiba.go.jp/KeibaWeb/TodayRaceInfo/RaceList?k_raceDate=2023%2f06%2f02&k_babaCode=18"
    chromeDriver.driver.get(current_url)
    
    # 翌日がなくなるまでループ
    while True:
        # print(current_url)
        chromeDriver.driver.get(current_url)
        tomorrow_elem = chromeDriver.get_element_by_class(chromeDriver.driver, "tomorrow")
        if(tomorrow_elem == None):
            break

        next_url = tomorrow_elem.get_attribute("href")
    
        # 成績リストを取得して番号
        # a_tag_list = chromeDriver.get_elements_by_tag_and_text(chromeDriver.driver, "a", "成績")
        a_tag_list = chromeDriver.get_elements_by_tag_and_text_except_class(chromeDriver.driver, "a", "成績", "disable")
        cur_url = chromeDriver.driver.current_url

        # 途中から開始した場合はエラーになりそう
        for race_no in range(len(a_tag_list)):  
            umaResult_list_by_race: List[umaResult] = []
            # influx登録用 Pointリスト
            point_list : Point = []

            result_url = cur_url.replace("RaceList", "RaceMarkTable")
            result_url = result_url + "&k_raceNo=" + str(race_no+1)
            chromeDriver.driver.get(result_url)

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
            table_bs_list = chromeDriver.get_elements_by_class(chromeDriver.driver, "bs")
            if table_bs_list != None and len(table_bs_list) < 4 : 
                print("error")
                sys.exit()

            # レース情報
            race_info_elem = chromeDriver.get_element_by_tag_and_contain_text(table_bs_list[1], "td", "")
            # print(race_info_elem.text)

            date_pattern = re.compile(r'(\d{4})年(\d{1,2})月(\d{1,2})日')
            distance_pattern = r'(\d+)ｍ'  # 数字（1回以上） + "ｍ"
            weather_pattern = r'天候：([^\s]+)'  # "天候：" + 空白以外の文字（1回以上）
            ground_condition_pattern = r'馬場：([^\s]+)'  # "馬場：" + 空白以外の文字（1回以上）

            date_match = date_pattern.search(race_info_elem.text)
            distance_match = re.search(distance_pattern, race_info_elem.text)
            weather_match = re.search(weather_pattern, race_info_elem.text)
            ground_condition_match = re.search(ground_condition_pattern, race_info_elem.text)

            print(f"{date_match.group(1)}, {date_match.group(2)}, {date_match.group(3)}")

            # 結果を表示
            if distance_match:
                distance = distance_match.group(1)
            if weather_match:
                weather = weather_match.group(1)
            if ground_condition_match:
                ground_condition = ground_condition_match.group(1) 

            # コーナ通過順
            # [['1,3,7,2,5,10,11,4,9,6,8'], ['1,3,7,10,2,5,11,4,6,9,8'], ['3,1,10,7,2,11,6,5,9,4,8'], ['3,2,11,7,10,1,6,9,4,5,8']]
            corner_elem = chromeDriver.get_element_by_tag_and_contain_text(table_bs_list[5], "td", "コーナー通過順")
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
            result_table_elem = chromeDriver.get_element_by_class(chromeDriver.driver, "dbtbl", 0)
            if (result_table_elem != None):
                tr_list = chromeDriver.get_elements_by_tag(result_table_elem, "tr")
                if len(tr_list) < 3:
                    print("error")
                    sys.exit()

                # trの1行目、2行目はヘッダなので飛ばす
                for tr in tr_list[2:]:
                    col_list = tr.find_elements(By.TAG_NAME, "td")

                    if len(col_list) > 14:
                        # 着順がない行はスキップ(取り消しのはず)
                        uma_result_data = umaResult()
                        try:
                            int(col_list[0].text)
                        except ValueError:
                            continue

                        uma_result_data.distance = distance
                        uma_result_data.weather = weather
                        uma_result_data.ground_condition = ground_condition

                        uma_result_data.position = int(col_list[0].text)
                        uma_result_data.horse_name = col_list[3].text
                        uma_result_data.umaban = int(col_list[2].text)
                        uma_result_data.affiliation = col_list[4].text
                        uma_result_data.age = int(col_list[5].text.split(" ")[1])
                        uma_result_data.sex = col_list[5].text.split(" ")[0]

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

                        uma_result_data.record = time_to_milliseconds(col_list[11].text)  # タイム 1:38.5　〇
                        uma_result_data.popularity = int(col_list[14].text)

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
                        umaResult_list_by_race.append(uma_result_data)

                # 父、母父の情報をとる
                tr_list = chromeDriver.get_elements_by_tag(result_table_elem, "tr")
                if len(tr_list) < 3:
                    print("error")
                    sys.exit()

                # trの1行目、2行目はヘッダなので飛ばす
                u_index = 2
                current_result_url = chromeDriver.driver.current_url
                while True:

                    # 元の画面に戻る
                    chromeDriver.driver.get(current_result_url)
                    result_table_elem = chromeDriver.get_element_by_class(chromeDriver.driver, "dbtbl", 0)
                    new_tr_list = chromeDriver.get_elements_by_tag(result_table_elem, "tr")
                    
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
                    a_tag_uma_list = chromeDriver.get_elements_by_tag(col_list[3], "a")
                    a_elem = a_tag_uma_list[0]
                    uma_url = a_elem.get_attribute("href")
                    uma_url = uma_url.replace("HorseMarkInfo","RaceHorseInfo") + "&k_activeCode=1"

                    chromeDriver.driver.get(uma_url)

                    pedigree_table_elem = chromeDriver.get_element_by_class(chromeDriver.driver, "pedigree", 0)
                    if (pedigree_table_elem != None):
                        pedigree_tr_list = chromeDriver.get_elements_by_tag(pedigree_table_elem, "tr")
                        if len(pedigree_tr_list) < 5:
                            print("error")
                            sys.exit()

                        # trの1行目、2行目はヘッダなので飛ばす
                        p_index = 1
                        for pedigree_tr in pedigree_tr_list[1:]:
                            col_list = pedigree_tr.find_elements(By.TAG_NAME, "td")
                            if p_index == 1:
                                # 一行目
                                umaResult_list_by_race[u_index-2].f_name = col_list[1].text
                            elif p_index == 3:
                                # 三行目の3
                                umaResult_list_by_race[u_index-2].mf_name = col_list[3].text
                            p_index = p_index+1

                    u_index = u_index + 1
                ##### while loop

                # for uma in umaResult_list_by_race:
                #     print(uma)
                # 1レース分ずつ登録していく
                # 一つのレース、馬番順に単勝オッズをリストに追加
                local_time = datetime( int(date_match.group(1)), int(date_match.group(2)), int(date_match.group(3)), 0, 0, 0)
                utc_time = local_time.astimezone(timezone.utc)

                for uma_result  in umaResult_list_by_race :
                    point_list.append( 
                        Point("浦和")
                        .tag("distance", uma_result.distance)
                        .tag("weather", uma_result.weather)
                        .tag("ground_condition", uma_result.ground_condition)
                        .tag("umaban", uma_result.umaban)
                        .tag("horse_name", uma_result.horse_name)
                        .tag("affiliation", uma_result.affiliation)
                        .tag("age", uma_result.age)
                        .tag("sex", uma_result.sex)
                        .tag("additional_weight", uma_result.additional_weight)
                        .tag("jokey_name", uma_result.jokey_name)
                        .tag("trainer_name", uma_result.trainer_name)
                        .tag("weight", uma_result.weight)
                        .tag("popularity", uma_result.popularity)
                        .tag("corner_position_rate", uma_result.corner_position_rate)       # 二桁で 0埋め！
                        .tag("f_name", uma_result.f_name)
                        .tag("mf_name", uma_result.mf_name)
                        .tag("position", uma_result.position)
                        .field("record", uma_result.record)
                        .field("position", uma_result.position)
                        .field("corner_position_rate", uma_result.corner_position_rate)  # 二桁で 0埋め！
                        .time(utc_time)
                    )
                
                if (len(point_list) > 0) :
                    influxClient.register_point_list(point_list)
                
    
        current_url = next_url

    ##### while loop
                    

        
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


        

# プログラム起動中ずっとこのループ処理をし続ける
def main_loop(mode) :

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

                chromeDriver = IpatSeleniumDriver(resource_path("temp"))
                chromeDriver.driver.get("https://www.jra.go.jp/keiba/")
                # 登録用のPointリストをwebから取得
                points_list = jra_odds_crawl(chromeDriver)

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

                chromeDriver = IpatSeleniumDriver(resource_path("temp"))
                chromeDriver.driver.get("https://www.keiba.go.jp/KeibaWeb/TodayRaceInfo/TodayRaceInfoTop")
                # 登録用のPointリストをwebから取得
                points_list = nar_odds_crawl(chromeDriver)

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





#
            

def main(mode) :
    # 起動メッセージ
    print("起動しました")
    print(f"実行時間は土曜日、日曜日 {START_HOUR}:00～{END_HOUR}:00 の間です。")
    # 一定時間ごとに crawl
    main_loop(mode)

def nar_odds_crawl_main(mode):
    # 起動メッセージ
    print("地方競馬オッズ収集プログラムを起動しました")
    print(f"実行時間は浦和競馬開催日 {NAR_START_HOUR}:00～{NAR_END_HOUR}:00 の間です。")
    # 一定時間ごとに crawl
    main_loop(mode)


def nar_race_result_crawl_main(mode):
    # 起動メッセージ
    print("地方競馬レース結果収集プログラムを起動しました")

    # 取得範囲を指定
    # デフォルトは実行時から過去1週間前までの結果
    # 1week


    nar_race_result_crawl()

# main
if __name__ == "__main__":
    # プログラムのタイムゾーンを日本にする
    locale.setlocale(locale.LC_TIME, "ja_JP.UTF-8")
    # オプションの設定
    parser = argparse.ArgumentParser(description='oddsの取得')
    parser.add_argument('-m', '--mode', choices=['jra-odds','nar-odds','jra-result','nar-result'])
    args = parser.parse_args()

    if args.mode == "jra-odds":
        main(args.mode)
    elif args.mode == "nar-odds":
        nar_odds_crawl_main(args.mode)
    elif args.mode == "jra-result":
        pass
    elif args.mode == "nar-result":

        # 浦和競馬場の去年のデータを集める
        # あとは今月分？
        nar_race_result_crawl_main(args.mode)

        pass
    


    # 騎手リーディングからジョッキー一覧をとる
    # jra_jokey_crawl()

