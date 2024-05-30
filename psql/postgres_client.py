from const import *
import psycopg2
from psycopg2.extensions import connection

# influx db への登録用 クラス
class PostgresClient:

    def __init__(self, bucket):
        pass

    def __del__(self):
        pass

    # まとめて登録する場合は Point の配列を作ってそれを渡す
    # 1R 30個くらいをまとめて送るのがよいか
    # 12R分 400個くらいをまとめておくるのがよいか
    def register_race_result(self, points) :
        pass


    ### 地方
    # レースごとに登録


    # 馬情報の登録