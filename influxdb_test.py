import influxdb_client
from influxdb_client import Point
from datetime import datetime, timezone, timedelta
import time
from influxdb_client.client.write_api import SYNCHRONOUS
import random

RACE_PLACE_ID = "race_place_id"
RACE_NO = "race_number"
TAG_COMBINE = "combine"
TAG_BETTING_TYPE = "betting_type"

#
# token = os.environ.get("INFLUXDB_TOKEN")
token = "BpuYs_ip6nKxvL2fcIBYqp8hxaz4x_94TgmKNeEjHwfq1SoIGPj87_IxyY47JjL8s558PyVO6vkAuVqBGTTEOQ=="
org = "organization"
url = "http://192.168.1.118:8086"

write_client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)

# bucket="race_odds"
bucket="bkt1"

write_api = write_client.write_api(write_options=SYNCHRONOUS)

# 指定した 開催場、レース番号、馬番、買い方のオッズを登録する
# まとめて一括登録はできないのかな..?
def register_odds(race_place_id, race_number, betting_type, combine, odds) :
    point = (
    Point(race_place_id)
    .tag(RACE_NO, race_number)
    .tag(TAG_BETTING_TYPE, betting_type)
    .tag(TAG_COMBINE, combine)
    .field("odds", odds)
    )
    write_api.write(bucket=bucket, org="organization", record=point)
#############
    
def register_random_odds(race_place_id, race_number, betting_type, combine) :
  rand_odds = random.uniform(0, 100)
  register_odds(race_place_id, race_number, betting_type, combine, rand_odds)


def register_point_list(points) :
    write_api.write(bucket=bucket, org="organization", record=points)

# for value in range(100):
  # for i in range(18):
  #   register_random_odds("A", 1, "単勝", i+1)
  #   register_random_odds("A", 2, "単勝", i+1)  
  #   register_random_odds("B", 1, "単勝", i+1)
  #   register_random_odds("C", 1, "単勝", i+1)

  # time.sleep(5) # separate points by 1 second

point_list = []
id_list = ["A","B","C"]

# 指定された日時を作成
local_time = datetime(2023, 1, 1, 0, 0, 0)

local_timezone = timezone(timedelta(hours=9))
# ローカルタイムをUTCに変換
utc_time = local_time.astimezone(timezone.utc)

print(utc_time)

for value in range(3):
  for i in range(len(id_list)):
    for j in range(12):
        for k in range(18):
          point_list.append(
            Point(id_list[i])
                .tag(RACE_NO, j+1)
                .tag(TAG_BETTING_TYPE, "単勝")
                .tag(TAG_COMBINE, k+1)
                .field("odds", random.uniform(0, 100))
                .field(TAG_COMBINE, k+1)
                .field(RACE_NO, j+1)
                # .time(utc_time)
          )
          # point_list.append(
          #   Point(id_list[i])
          #       .tag(RACE_NO, j+1)
          #       .tag(TAG_BETTING_TYPE, "複勝")
          #       .tag(TAG_COMBINE, k+1)
          #       .field("odds", random.uniform(0, 100))
          # )

# ジョッキーも混ぜてみるとか

  register_point_list(point_list)

  time.sleep(5)