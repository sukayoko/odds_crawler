


from const import *
import influxdb_client, os, time
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS


# influx db への登録用 クラス
class InfluxDBLocalClient:
    #
    token = "BpuYs_ip6nKxvL2fcIBYqp8hxaz4x_94TgmKNeEjHwfq1SoIGPj87_IxyY47JjL8s558PyVO6vkAuVqBGTTEOQ=="
    org = "organization"
    url = "http://192.168.1.118:8086"
    bucket="test"
    write_client = None
    write_api = None

    


    def __init__(self, bucket):
        self.bucket = bucket
        self.write_client = influxdb_client.InfluxDBClient(url=self.url, token=self.token, org=self.org)
        self.write_api = self.write_client.write_api(write_options=SYNCHRONOUS)

    def __del__(self):
        pass


    # 指定した 開催場、レース番号、馬番、買い方のオッズを登録する
    # まとめて一括登録はできないのかな..?
    # register_odds("A", 1, "単勝", i+1, 2.3)
    def register_odds(self, race_place_id, race_number, betting_type, combine, odds) :
        point = (
        Point(race_place_id)
        .tag(RACE_NO, race_number)
        .tag(TAG_BETTING_TYPE, betting_type)
        .tag(TAG_COMBINE, combine)
        .field("odds", odds)
        )
        self.write_api.write(bucket=self.bucket, org="organization", record=point)

    # まとめて登録する場合は Point の配列を作ってそれを渡す
    # 1R 30個くらいをまとめて送るのがよいか
    # 12R分 400個くらいをまとめておくるのがよいか
    def register_point_list(self, points) :
        self.write_api.write(bucket=self.bucket, org="organization", record=points)