from const import *
import psycopg2
from psycopg2.extensions import connection
from race_result_obj import NarRaceResultObj
from typing import List

# influx db への登録用 クラス
class PostgresClient:

    def __init__(self):
        pass

    def __del__(self):
        pass

    ### 地方
    # レースごとに登録
    def register_nar_race_result(self, nar_race_result_list : List[NarRaceResultObj]) :
        # PostgreSQLデータベースへの接続
        conn = psycopg2.connect(
            dbname="chessdb",
            user="root",
            password="secret",
            host="192.168.56.18",
            port="5432"
        )
        # カーソルオブジェクトを作成
        cur = conn.cursor()
        # レコードを挿入するためのSQLクエリ
        insert_query = """
        INSERT INTO nar_race_results (
            date, ba, race_num, distance, weather, ground_condition, rule,
            horse_name, position, umaban, age, sex, birthday, f_name, ff_name,
            mf_name, farm, affiliation, jokey_name, trainer_name, owner_name,
            additional_weight, weight, record, last_three_furlong, popularity,
            corner_position_rate, rounded_weight, pre_race_interval_week
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s,
            %s, %s, %s
        )
        """

        for race_result_row in nar_race_result_list :
            data = (
                race_result_row.date,  # date
                race_result_row.ba,                         # ba
                race_result_row.race_num,                               # race_num
                race_result_row.distance,                            # distance
                race_result_row.weather,                         # weather
                race_result_row.ground_condition,                          # ground_condition
                race_result_row.rule,                          # rule
                race_result_row.horse_name,                    # horse_name
                race_result_row.position,                               # position
                race_result_row.umaban,                               # umaban
                race_result_row.age,                               # age
                race_result_row.sex,                          # sex
                race_result_row.birthday,                         # birthday
                race_result_row.f_name,                   # f_name
                race_result_row.ff_name,              # ff_name
                race_result_row.mf_name,     # mf_name
                race_result_row.farm,                     # farm
                race_result_row.affiliation,              # affiliation
                race_result_row.jokey_name,                   # jokey_name
                race_result_row.trainer_name,                  # trainer_name
                race_result_row.owner_name,                    # owner_name
                race_result_row.additional_weight,                            # additional_weight
                race_result_row.weight,                           # weight
                race_result_row.record,                          # record (in milliseconds)
                race_result_row.last_three_furlong,                            # last_three_furlong
                race_result_row.popularity,                               # popularity
                race_result_row.corner_position_rate,                              # corner_position_rate
                race_result_row.rounded_weight,                           # rounded_weight
                race_result_row.pre_race_interval_week                                # pre_race_interval_week
            )

            # データを挿入
            cur.execute(insert_query, data)

        # トランザクションをコミット
        conn.commit()

        # カーソルと接続を閉じる
        cur.close()
        conn.close()

        print("レコードが正常に挿入されました。")




    # 馬情報の登録