
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
        ba_str = 5

        # 1年分日付でループ
        # https://race.netkeiba.com/race/result.html?race_id=202306010101&mode=result
        # https://race.netkeiba.com/top/payback_list.html?kaisai_date=20230105

        # 06 は中山 01 は 1回 02 は二日目
        # https://race.netkeiba.com/top/payback_list.html?kaisai_id=2023060102&kaisai_date=20230107
        
        # 存在しない場合もある
        try: 
            # 回、日、レースでループ　
            # 存在しない場合？
            for range(10) :
                # 1回1R が存在しないなら終了
                for range(19):
                    # n回1R が存在しないなら次
                    for range(13):
                        # nRが存在しないなら次                
                        date_string = current_date.strftime('%Y%m%d')
                        print(date_string)


                        current_date += timedelta(days=1)

                        # 開催の情報ページへ遷移
                        self.driver.get(kaisaiUrlAlias + date_string)

                        # https://race.netkeiba.com/race/result.html?race_id=202305010101&mode=result
                        # 2023年　05 が東京 01 が 1回 01 が 1日 01 が 1R

                        # 回

                        # 

                        # パスが異なる場合　次へ
                        result_table_elem = self.get_element_by_class(self.driver, "ResultTableWrap")
                        if result_table_elem != None :
                            pass
                        else : 
                            # 存在する場合
                            # RaceKaisaiWrap の Colクラスの li 要素一覧
                            # aタグの title が　東京



                            # レース結果詳細




                    pass

            pass
        except NoSuchElementException:
            pass