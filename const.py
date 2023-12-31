"""
Constant types in Python.
"""

from enum import Enum

#### 定数
CONFIG_KEY = "as"
# プログラムの実行時間範囲と実行間隔
START_HOUR = 0
END_HOUR = 24

INTERVAL_MINUTES = 1


RACE_INFO_URL = (
   "https://www.keiba.go.jp/KeibaWeb_IPAT/TodayRaceInfo/TodayRaceInfoTop_ipat"
)

########################
### よく変更するであろう定数
# アクセス数を増やすためのループ回数  LOOP_CNT_MAX以上を設定した場合はエラー
LOOP_CNT = 3

IPAT_SOKU_ID = "99212895"
IPAT_APAT_ID = ""
IPAT_PW = "9999"
IPAT_TEST_PW = "1234"
IPAT_PARS = "9999"

LIMIT_IPAT_ID = "99275002"
LIMIT_IPAT_PW = "9999"
LIMIT_IPAT_PARS = "9999"
LIMIT_TEST_PW = "1234"

# 入金パスワード
# 入金金額・閾値


# URLリスト
LIMIT_URL = "https://limit.ipat.jra.go.jp/"
GALAHO_URL = "https://g.ipat.jra.go.jp/"
########################