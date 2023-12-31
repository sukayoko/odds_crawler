# セレニウムのドライバークラス
# 引数によって　動作モードを切り替えたい
# TODO ipat用にクラスを作った方がよい
from selenium import webdriver
import time
import sys
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

# Selenium クラス
class SeleniumDriver:
    # ブラウザ ドライバ
    browser_path = ""
    driver_path = ""
    driver = None

    # コンストラクタ
    def __init__(self):
        # ブラウザ指定 TODO: ブラウザの条件分岐
        self.browser_path = self.resource_path('browser/chrome/chrome.exe')
        self.driver_path = self.resource_path('driver/chrome/chromedriver.exe')

        options = webdriver.ChromeOptions()

        # ブラウザを起動せずに実行するオプション
        # options.add_argument('--headless')

        # 以下のエラーが出るので指定
        # Cloud management controller initialization aborted as CBCM is not enabled. 
        # Please use the `--enable-chrome-browser-cloud-management` command line flag to enable it 
        # if you are not using the official Google Chrome build.
        options.add_argument('--enable-chrome-browser-cloud-management')

        options.binary_location = self.browser_path
        service = ChromeService(executable_path=self.driver_path)
        self.driver = webdriver.Chrome(options=options, service=service)
        
        # 指定した要素が見つかるまでの待ち時間を設定する 今回は最大10秒待機する
        # 待機しても要素が見つからない場合、 NoSuchElementException が出る
        self.driver.implicitly_wait(1)

    def __del__(self):
        self.driver.quit()
    
    ## デストラクタと分ける必要ない気もする
    def end(self):
        self.driver.quit()

    # exeファイルにしたときのパス指定
    def resource_path(self, relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.dirname(__file__)
        return os.path.join(base_path, relative_path)

    def frame_function(self, delaymill) :
        time.sleep(delaymill / 1000)

    # 画面操作の utility
    # ガラホ用
    # 特定の要素配下の
    # 特定のvalueを持つボタン(input)をクリックする
    # 要素をクリックしたら true
    def search_input_by_value_and_click(self, search_value):
        if(self.driver != None):
            button_elements = self.driver.find_elements(By.TAG_NAME, "input")
            for input_element in button_elements :
                if (input_element.get_attribute("value") == search_value):
                    input_element.click()
                    return True
        return False
    
    # ブラウザ用
    # 特定の要素配下の
    # 特定の textを持つボタン(button)をクリックする
    # または、
    # 特定の文字列<span>を持つボタン(button)をクリックする
    # 要素をクリックしたら true
    def search_button_by_text_and_click(self, search_txt):
        if(self.driver != None):
            button_elements = self.driver.find_elements(By.TAG_NAME, "button")
            for button_element in button_elements :
                if (button_element.text == search_txt) :
                    button_element.click()
                    return True


        # 見つからなかったら False        
        return False
    

    # スマホ用
    # 特定のclass　特定の文字列の要素をクリックする 
    # 要素をクリックしたら true
    def search_and_click_by_class(self, class_name, search_text = ""):
        if(self.driver != None):
            # class は単一でない可能性
            class_elements = self.driver.find_elements(By.CLASS_NAME, class_name)
            for cl_elem in class_elements :
                if(cl_elem.text == search_text):
                    cl_elem.click()                   
                    return True
        # 見つからなかったら False        
        return False
    
    # スマホ用
    # 特定のid 
    # 要素をクリックしたら true
    def search_and_click_by_id(self, id_name):
        if(self.driver != None):
            # class は単一でない可能性
            id_elements = self.driver.find_element(By.ID, id_name)
            if(id_elements):
                    id_elements.click()                   
                    return True
            else :
            # 見つからなかったら False        
                return False

    # スマホ用
    # 特定のclassのテキストを取得する
    # classだけだと特定できないので親要素も引数にしている
    # 要素を取得したら true
    def search_text_by_class(self, parent_elem, class_name):
        if(self.driver != None):
            # class は単一でない可能性
            class_elements = parent_elem.find_elements(By.CLASS_NAME, class_name)
            for cl_elem in class_elements :
                return cl_elem.text
        # 見つからなかったら False        
        return ""

    # スマホ用
    # 特定のclassを取得する
    # n 番目の classであることも指定可能 省略した場合は 1番目
    # 要素を取得したら true
    def search_element_by_class(self, class_name, get_index = 0):
        if(self.driver != None):
            # class は単一でない可能性
            class_elements = self.driver.find_elements(By.CLASS_NAME, class_name)
            idx = 0
            for cl_elem in class_elements :
                if (idx == get_index):
                    return cl_elem
                else :
                    idx = idx + 1

        # 見つからなかったら False        
        return None


    # 特定のidの inputに値を指定する
    # 指定出来たら True
    def set_value_input_by_id(self, id, set_txt) :
        if(self.driver != None):
            input_element = self.driver.find_element(By.ID, id)
            if (input_element) :
                input_element.send_keys(set_txt)
                return True

        # 見つからなかったら False        
        return False
    
    # 指定した要素は以下のaタグ一覧を出す
    def print_element_by_a_text(self, root_elem) :
        atag_elements = root_elem.find_elements(By.TAG_NAME, "a")
        for a_elem in atag_elements :
            print("'" + a_elem.text + "'")

    # 情報ページで開催場名一覧を取得する
    def get_ba_list_from_atag(self, root_elem) :
        ba_list = []
        atag_elements = root_elem.find_elements(By.TAG_NAME, "a")
        for a_elem in atag_elements :
            ba_list.append(a_elem.text)
        
        return ba_list
    
    # オッズページで開催場名一覧を取得する
    def get_ba_list_from_oddspage(self, root_elem) :
        ba_elem_list = []
        atag_elements = root_elem.find_elements(By.TAG_NAME, "a")
        for a_elem in atag_elements :
            ba_elem_list.append(a_elem)
        
        return ba_elem_list
    

    # 特定の文字列を持つ aタグを捜しクリックする(JRA HP用)
    def click_element_by_a_text(self, text) :
        atag_elements = self.driver.find_elements(By.TAG_NAME, "a")
        for a_elem in atag_elements :
            # print("'" + a_elem.text + "'")
            if (a_elem.text == text) :
                a_elem.click()
                return True
        
        return False
    
    # 特定の文字列を持つ aタグを捜しクリックする(JRA HP用)
    def click_element_by_span_text(self, text) :
        atag_elements = self.driver.find_elements(By.TAG_NAME, "span")
        for a_elem in atag_elements :
            # print("'" + a_elem.text + "'")
            if (a_elem.text == text) :
                a_elem.click()
                return True
        
        return False
    



    # 特定のクラス名を持つ要素を取得(単一)
    def get_element_by_class(self, root_elem, class_name, get_index = 0):
        if(self.driver != None):
            # class は単一でない可能性
            class_elements = root_elem.find_elements(By.CLASS_NAME, class_name)
            idx = 0
            for cl_elem in class_elements :
                if (idx == get_index):
                    return cl_elem
                else :
                    idx = idx + 1
            return None
    
    # 特定のクラス名を持つ要素を取得(複数)
    def get_elements_by_class(self, root_elem ,class_name):
        if(self.driver != None):
            # class は単一でない可能性
            class_elements = root_elem.find_elements(By.CLASS_NAME, class_name)
            if (len(class_elements) > 0):
                return class_elements
            else :
                return None
            
    def test_elem(self) :
        e = self.driver.find_element(By.XPATH, "//*[@id=\"race_list\"]/tbody/tr[1]/td[3]/div/div[1]/a")
        e.click()
        print(e)

    # JRAのオッズメニューからオッズ一覧を取得する
    def get_odds_list_from_table(self, root_elem, class_name) :
        odds_list = []
        tdlist = root_elem.find_elements(By.CLASS_NAME, class_name)

        if len(tdlist) > 0:
            for td in tdlist:
                odds_list.append(td.text)
            return odds_list
        else:
            return None

    # JRAのオッズメニューからレース番号一覧を取得する
    def get_race_list_from_page(self) :
        race_elem = self.get_element_by_class(self.driver, "race-num")
        race_num_list = race_elem.find_elements(By.TAG_NAME, "a")

        if len(race_num_list) > 0:
            return race_num_list
        else:
            return None
