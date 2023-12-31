import influxdb_client, os, time
from influxdb_client import InfluxDBClient, Point, WritePrecision
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

bucket="race_odds"

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

for value in range(100):
  for i in range(18):
    register_random_odds("A", 1, "単勝", i+1)
    register_random_odds("A", 2, "単勝", i+1)  
    register_random_odds("B", 1, "単勝", i+1)
    register_random_odds("C", 1, "単勝", i+1)

  time.sleep(5) # separate points by 1 second

