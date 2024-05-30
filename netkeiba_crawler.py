
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

        self.driver.execute_cdp_cmd('Network.enable', {})
        self.driver.execute_cdp_cmd('Network.setBlockedURLs', {
            'urls': [
            'images.taboola.com',
            'sg-trc-events.taboola.com',
            'bidder.criteo.com',
            'pippio.com',
            'tg.socdm.com',
            'hbopenbid.pubmatic.com',
            'usermatch.krxd.net',
            'aax.amazon-adsystem.com',
            'ib.adnxs.com',
            'secure.adnxs.com',
            'fastlane.rubiconproject.net'
            'securepubads.g.doubleclick.net'
            'aladdin.genieesspv.com',
            'shb.richaudience.com',


            # '*.png',
            '*.jpg',
            '*.gif',
        ]})

    def __del__(self):
        return super().__del__()

    # 本日のレース情報を取得
    def save_race_info_to_influxdb(self):

        kaisaiUrlAlias = "https://race.netkeiba.com/top/payback_list.html?kaisai_date="

        # 東京の場合
        ba_str = "05"
        skip_flg = False
        
        # 05 は東京 01 は 1回 02 は二日目 03 は第三レース
        # https://race.netkeiba.com/race/result.html?race_id=202305010203&mode=result
        
        # 存在しない場合もある
        try: 
            # 回、日、レースでループ
            # 開催日　は　最大5 ?
            for kaisai_num in range(1, 6):
                if(skip_flg) :
                    skip_flg = False

                # 開催日数は最大12日
                for day_num in range(1, 13):
                    if(skip_flg):
                        break

                    # 開催レースは最大12
                    # for race_num in range(1, 13):
                    for race_num in range(1, 2):
                        print("第" + str(kaisai_num) + "回" +  str(day_num) + "日" +  str(race_num) + "R") 
                        # n回n日nRが存在しないなら次
                        chk_url = "https://race.netkeiba.com/race/result.html?race_id=2023" + ba_str + str(kaisai_num).zfill(2) + str(day_num).zfill(2) + str(race_num).zfill(2) + "&mode=result"
                        # nレースの開催の情報ページへ遷移
                        self.driver.get(chk_url)
                        result_table_elem = self.get_element_by_class(self.driver, "ResultTableWrap")
                        if result_table_elem != None :
                            print("このレース情報は存在しません")
                            skip_flg = True
                            break

                        # 馬一覧を取る

                        # 馬毎に情報

                        # 馬の父
                        # 馬の母父


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