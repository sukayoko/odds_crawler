import locale,argparse,time
from const import *
from ipat_selenium_driver import IpatSeleniumDriver
from netkeiba_crawler import NetkeibaCrawler
from nar_race_result_crawl import NarRaceResultCrawler
from nar_race_card_generator import NarRaceCardGenerator 
                    
# main
if __name__ == "__main__":
    # プログラムのタイムゾーンを日本にする
    locale.setlocale(locale.LC_TIME, "ja_JP.UTF-8")
    # オプションの設定
    parser = argparse.ArgumentParser(description='oddsの取得')
    parser.add_argument('-m', '--mode', choices=['jra-odds','nar-odds','jra-result','nar-result','jar-card', 'nar-card'])
    parser.add_argument('-d', '--dev', default=False, choices=[True,False])
    # TODO 対象日付
    args = parser.parse_args()

    if args.mode == "jra-odds":
        # main(args.mode)
        pass
    elif args.mode == "nar-odds":
        # nar_odds_crawl_main(args.mode)
        pass
    elif args.mode == "jra-result":

        # とりあえず一回分
        # netkeiba_crawler = NetkeibaCrawler("東京")
        # netkeiba_crawler.save_race_info_to_influxdb()

        pass
    elif args.mode == "nar-result":
        print("地方競馬レース結果収集プログラムを起動しました")

        # 場名を指定して呼び出す
        narRaceResultCrawler =  NarRaceResultCrawler("temp", "大井", args.dev)
        narRaceResultCrawler.nar_race_result_crawl_main()

        pass
    elif args.mode == "jra-card":
        pass
    elif args.mode == "nar-card":
        print("地方競馬レース結果収集プログラムを起動しました")

        # 場名を指定して呼び出す
        narRaceCardGenerator =  NarRaceCardGenerator("temp", args.dev)
        narRaceCardGenerator.nar_race_card_generate_main("2024-06-03","大井")

        pass


# ジョッキー一覧を取得
# def jra_jokey_crawl():
#     chromeDriver = IpatSeleniumDriver("temp")
#     chromeDriver.driver.get("https://www.jra.go.jp/datafile/leading/")

#     chromeDriver.click_element_by_a_text("騎手")
#     # ul_elem = chromeDriver.get_element_by_class(chromeDriver.driver, "data_line_list")

#     while True :
#         j_list = chromeDriver.get_jokeis_list_from_table(chromeDriver.driver, "name")

#         for j_name in j_list:
#             print(j_name)

#         if (chromeDriver.click_element_by_a_text("次の20件")) :
#             time.sleep(1)
#         else :
#             break 