
# セレニウムのドライバークラス
# 引数によって　動作モードを切り替えたい
from selenium_driver import SeleniumDriver
from const import *
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from datetime import datetime, timedelta

# Selenium クラス
class NetkeibaCrawler(SeleniumDriver) :
    # 場名
    ba = ""

    # コンストラクタ
    def __init__(self, baStr):
        self.ba = baStr
        super().__init__()

    def __del__(self):
        return super().__del__()

    # 本日のレース情報を取得
    def save_race_info_to_influxdb(self):

        kaisaiUrlAlias = "https://race.netkeiba.com/top/payback_list.html?kaisai_date="

        # 東京の場合
        ba_str = "05"
        
        # 06 は中山 01 は 1回 02 は二日目
        # https://race.netkeiba.com/top/payback_list.html?kaisai_id=2023060102&kaisai_date=20230107
        
        # 存在しない場合もある
        try: 
            # 回、日、レースでループ
            # 存在しない場合？
            for kaisai_num in range(1, 6):
                print("kaisai_num" + kaisai_num)
                # n回1日1R が存在しないなら終了
                chk_url = "https://race.netkeiba.com/race/result.html?race_id=2023" + ba_str + str(kaisai_num).zfill(2) + "0101" + "&mode=result"
                if ( not self.chk_race_result_exist(chk_url) ):
                    continue

                for day_num in range(1, 15):
                    # n日1R が存在しないなら次
                    print("day_num" + day_num)
                    chk_url = "https://race.netkeiba.com/race/result.html?race_id=2023" + ba_str + str(kaisai_num).zfill(2) + str(day_num).zfill(2) + "01" + "&mode=result"
                    if ( not self.chk_race_result_exist(chk_url) ):
                        continue

                    # TODO: ここでレースの一覧を取得すべき？  

                    for race_num in range(1, 13):
                        print("race_num" + race_num) 
                        # nRが存在しないなら次
                        chk_url = "https://race.netkeiba.com/race/result.html?race_id=2023" + ba_str + str(kaisai_num).zfill(2) + str(day_num).zfill(2) + str(race_num).zfill(2) + "&mode=result"
                        if ( not self.chk_race_result_exist(chk_url) ):
                             continue

                        # 開催の情報ページへ遷移
                        

                        # https://race.netkeiba.com/race/result.html?race_id=202305010101&mode=result
                        # 2023年 05 が東京 01 が 1回 01 が 1日 01 が 1R

                        # 回

                        # 

                        # パスが異なる場合 次へ
                        result_table_elem = self.get_element_by_class(self.driver, "ResultTableWrap")
                        if result_table_elem != None :
                            pass
                        else : 
                            pass
                            # 存在する場合
                            # RaceKaisaiWrap の Colクラスの li 要素一覧
                            # aタグの title が 東京



                            # レース結果詳細

        except NoSuchElementException:
            pass

    # レース詳細が存在しないばあい False
    def chk_race_result_exist(self, url_str : str):
        self.driver.get(url_str)
        result_table_elem = self.get_element_by_class(self.driver, "ResultTableWrap")
        if result_table_elem != None :
            return True
        else :
            return False