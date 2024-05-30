# セレニウムのドライバークラス
# 引数によって　動作モードを切り替えたい
# TODO ipat用にクラスを作った方がよい
from selenium_driver import SeleniumDriver
import time, sys, os
from const import *
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

def resource_path(relative_path):
    # TODO exe化する時と開発するときでパスが変わる
    try:
        base_path = sys._MEIPASS
        # exe化用（ダブルクリックで実行したとき、実行ファイルの配置場所のパスとなる）
        # base_path = os.getcwd()
    except Exception:
        base_path = os.path.dirname(__file__)
    return os.path.join(base_path, relative_path)

# Selenium クラス
class IpatSeleniumDriver(SeleniumDriver) :

    # アクセス先のURL
    target_url = ""
    dir_path = ""

    # コンストラクタ
    def __init__(self, file_path):
        self.dir_path = resource_path(file_path)
        super().__init__()

    def __del__(self):
        return super().__del__()

        # 本日のレース情報を取得
    def get_race_info(self, race_info_url):
        self.driver.get(race_info_url)

        # 存在しない場合もある
        try:

            table = self.driver.find_element(by=By.XPATH, value="//table[@class='course']")

            target_header = "本日"
            header_cells = table.find_elements(by=By.TAG_NAME, value="th")

            target_column_index = -1
            for index, cell in enumerate(header_cells):
                if target_header in cell.text:
                    target_column_index = index

            if not target_column_index == -1 :
                column_cells = table.find_elements(by=By.XPATH, value=f".//tr/td[{target_column_index + 1}]")  # インデックスは1から始まるため +1

                link_list = []
                for cell in column_cells:
                    link_elements = cell.find_elements(by=By.TAG_NAME, value="a")
                    if not link_elements == None :
                        for link_elem in link_elements:
                            link_url = link_elem.get_attribute("href")
                            print(f"リンクのURL: {link_url}")
                            link_list.append(link_url)

                        
                for index, link in enumerate(link_list):
                    # レース数を取得しても良いか

                    # リンク先の情報を取得して保存
                    self.save_odds_info(index, link)
                    pass
            else:
                # 飛ばす
                pass
        except NoSuchElementException:
            pass


    # 本日のレースの情報を取得
    def save_odds_info(self, index_num, race_info_url):
        text_list = []

        #   URL を一部加工してオッズ画面へ 
        #   https://www.keiba.go.jp/KeibaWeb_IPAT/TodayRaceInfo/RaceList_ipat?k_raceDate=2023%2f12%2f21&k_babaCode=27
        #   https://www.keiba.go.jp/KeibaWeb_IPAT/TodayRaceInfo/OddsTanFuku_ipat?k_raceDate=2023%2f12%2f21&k_raceNo=1&k_babaCode=27
        odds_info_url = race_info_url.replace('RaceList_ipat', 'OddsTanFuku_ipat')
        # 末尾にレースコード
        odds_info_url = odds_info_url + "&k_raceNo=10"

        print("オッズ:" + odds_info_url)
        self.driver.get(odds_info_url)
        # 発走時刻の一覧を取得
        ## レース番号と発走時刻
        row_cells = self.driver.find_elements(by=By.XPATH, value="/html/body/div[3]/article/div/div/ul/li/ul/li/form/table/tbody/tr")

        for row in row_cells:
            columns = row.find_elements(by=By.TAG_NAME, value="td")
            if len(columns) >= 4:
                odds_value = columns[3].text

                print(odds_value)
        
                # print(f"{first_column_value} 発走時刻 {second_column_value}")
                text_list.append(f"{odds_value}")

        self.save_txt_file(index_num, text_list)

    def save_txt_file(self, file_name, text_list) :
        # print(f"{self.dir_path}/{file_name}.txt")
        with open(f"{self.dir_path}/{file_name}.txt", "a") as file:
            file.write( ', '.join(text_list) + "\n")
