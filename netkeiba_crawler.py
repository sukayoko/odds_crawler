
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
            # '*.jpg',
            # '*.gif',
        ]})

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
                print("kaisai_num" + str(kaisai_num))
                # n回1日1R が存在しないなら終了
                chk_url = "https://race.netkeiba.com/race/result.html?race_id=2023" + ba_str + str(kaisai_num).zfill(2) + "0101" + "&mode=result"
                if ( not self.chk_race_result_exist(chk_url) ):
                    continue

                for day_num in range(1, 15):
                    # n日1R が存在しないなら次
                    print("day_num" + str(day_num))
                    chk_url = "https://race.netkeiba.com/race/result.html?race_id=2023" + ba_str + str(kaisai_num).zfill(2) + str(day_num).zfill(2) + "01" + "&mode=result"
                    if ( not self.chk_race_result_exist(chk_url) ):
                        continue

                    for race_num in range(1, 13):
                        print("race_num" + str(race_num)) 
                        # nRが存在しないなら次
                        chk_url = "https://race.netkeiba.com/race/result.html?race_id=2023" + ba_str + str(kaisai_num).zfill(2) + str(day_num).zfill(2) + str(race_num).zfill(2) + "&mode=result"
                        if ( not self.chk_race_result_exist(chk_url) ):
                             continue

                        # nレースの開催の情報ページへ遷移
                        self.driver.get(chk_url)

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