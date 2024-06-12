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
    ##############################################################################################

###########################################################################
    def get_sex_stats(self, ba, distance, ground_condition, rule, sex):
        try:
            # PostgreSQLデータベースへの接続
            conn = psycopg2.connect(
                dbname="chessdb",
                user="root",
                password="secret",
                host="192.168.56.18",
                port="5432"
            )
            cur = conn.cursor()

            # SQLクエリ
            query = """
            SELECT
                AVG(position) AS average_position,
                COUNT(*) AS total_races,
                AVG(corner_position_rate) AS avg_corner_position_rate, 
                COUNT(*) AS total_races,
                AVG(last_three_furlong ) AS avg_last_three_furlong_rate,
                COUNT(*) AS total_races
            FROM
                nar_race_results
            WHERE
                ba = %s AND
                distance = %s AND
                ground_condition = %s AND
                rule = %s AND
                sex = %s
            GROUP BY
                sex;
            """

            # クエリの実行
            cur.execute(query, (ba, distance, ground_condition, rule, sex))

            # 結果を取得
            results = cur.fetchall()

            # 接続を閉じる
            cur.close()
            conn.close()

            return results
        
        except Exception as e:
            print(f"Error: {e}")
            return None

    def get_age_stats(self, ba, distance, ground_condition, rule, age):
        try:
            # PostgreSQLデータベースへの接続
            conn = psycopg2.connect(
                dbname="chessdb",
                user="root",
                password="secret",
                host="192.168.56.18",
                port="5432"
            )
            cur = conn.cursor()

            # SQLクエリ
            query = """
            SELECT
                AVG(position) AS average_position,
                COUNT(*) AS total_races,
                AVG(corner_position_rate) AS avg_corner_position_rate, 
                COUNT(*) AS total_races,
                AVG(last_three_furlong ) AS avg_last_three_furlong_rate,
                COUNT(*) AS total_races
            FROM
                nar_race_results
            WHERE
                ba = %s AND
                distance = %s AND
                ground_condition = %s AND
                rule = %s AND
                age = %s
            GROUP BY
                age;
            """

            # クエリの実行
            cur.execute(query, (ba, distance, ground_condition, rule, age))

            # 結果を取得
            results = cur.fetchall()

            # 接続を閉じる
            cur.close()
            conn.close()

            return results
        
        except Exception as e:
            print(f"Error: {e}")
            return None

    def get_owner_name_stats(self, ba, distance, ground_condition, rule, owner_name):
            try:
                # PostgreSQLデータベースへの接続
                conn = psycopg2.connect(
                    dbname="chessdb",
                    user="root",
                    password="secret",
                    host="192.168.56.18",
                    port="5432"
                )
                cur = conn.cursor()

                # SQLクエリ
                query = """
                SELECT
                    AVG(position) AS average_position,
                    COUNT(*) AS total_races,
                    AVG(corner_position_rate) AS avg_corner_position_rate, 
                    COUNT(*) AS total_races,
                    AVG(last_three_furlong ) AS avg_last_three_furlong_rate,
                    COUNT(*) AS total_races
                FROM
                    nar_race_results
                WHERE
                    ba = %s AND
                    distance = %s AND
                    ground_condition = %s AND
                    rule = %s AND
                    owner_name = %s
                GROUP BY
                    owner_name;
                """

                # クエリの実行
                cur.execute(query, (ba, distance, ground_condition, rule, owner_name))

                # 結果を取得
                results = cur.fetchall()

                # 接続を閉じる
                cur.close()
                conn.close()

                return results
            
            except Exception as e:
                print(f"Error: {e}")
                return None

    def get_farm_stats(self, ba, distance, ground_condition, rule, farm):
            try:
                # PostgreSQLデータベースへの接続
                conn = psycopg2.connect(
                    dbname="chessdb",
                    user="root",
                    password="secret",
                    host="192.168.56.18",
                    port="5432"
                )
                cur = conn.cursor()

                # SQLクエリ
                query = """
                SELECT
                    AVG(position) AS average_position,
                    COUNT(*) AS total_races,
                    AVG(corner_position_rate) AS avg_corner_position_rate, 
                    COUNT(*) AS total_races,
                    AVG(last_three_furlong ) AS avg_last_three_furlong_rate,
                    COUNT(*) AS total_races
                FROM
                    nar_race_results
                WHERE
                    ba = %s AND
                    distance = %s AND
                    ground_condition = %s AND
                    rule = %s AND
                    farm = %s
                GROUP BY
                    farm;
                """

                # クエリの実行
                cur.execute(query, (ba, distance, ground_condition, rule, farm))

                # 結果を取得
                results = cur.fetchall()

                # 接続を閉じる
                cur.close()
                conn.close()

                return results
            
            except Exception as e:
                print(f"Error: {e}")
                return None

    def get_jockey_stats(self, ba, distance, ground_condition, rule, jokey_name):
        try:
            # PostgreSQLデータベースへの接続
            conn = psycopg2.connect(
                dbname="chessdb",
                user="root",
                password="secret",
                host="192.168.56.18",
                port="5432"
            )
            cur = conn.cursor()

            # SQLクエリ
            query = """
            SELECT
                AVG(position) AS average_position,
                COUNT(*) AS total_races,
                AVG(corner_position_rate) AS avg_corner_position_rate, 
                COUNT(*) AS total_races,
                AVG(last_three_furlong ) AS avg_last_three_furlong_rate,
                COUNT(*) AS total_races
            FROM
                nar_race_results
            WHERE
                ba = %s AND
                distance = %s AND
                ground_condition = %s AND
                rule = %s AND
                jokey_name = %s
            GROUP BY
                jokey_name;
            """

            # クエリの実行
            cur.execute(query, (ba, distance, ground_condition, rule, jokey_name))

            # 結果を取得
            results = cur.fetchall()

            # 接続を閉じる
            cur.close()
            conn.close()

            return results
        
        except Exception as e:
            print(f"Error: {e}")
            return None

    def get_trainer_name_stats(self, ba, distance, ground_condition, rule, trainer_name):
        try:
            # PostgreSQLデータベースへの接続
            conn = psycopg2.connect(
                dbname="chessdb",
                user="root",
                password="secret",
                host="192.168.56.18",
                port="5432"
            )
            cur = conn.cursor()

            # SQLクエリ
            query = """
            SELECT
                AVG(position) AS average_position,
                COUNT(*) AS total_races,
                AVG(corner_position_rate) AS avg_corner_position_rate, 
                COUNT(*) AS total_races,
                AVG(last_three_furlong ) AS avg_last_three_furlong_rate,
                COUNT(*) AS total_races
            FROM
                nar_race_results
            WHERE
                ba = %s AND
                distance = %s AND
                ground_condition = %s AND
                rule = %s AND
                trainer_name = %s
            GROUP BY
                trainer_name;
            """

            # クエリの実行
            cur.execute(query, (ba, distance, ground_condition, rule, trainer_name))

            # 結果を取得
            results = cur.fetchall()

            # 接続を閉じる
            cur.close()
            conn.close()

            return results
        
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    def get_f_name_stats(self, ba, distance, ground_condition, rule, f_name):
        try:
            # PostgreSQLデータベースへの接続
            conn = psycopg2.connect(
                dbname="chessdb",
                user="root",
                password="secret",
                host="192.168.56.18",
                port="5432"
            )
            cur = conn.cursor()

            # SQLクエリ
            query = """
            SELECT
                AVG(position) AS average_position,
                COUNT(*) AS total_races,
                AVG(corner_position_rate) AS avg_corner_position_rate, 
                COUNT(*) AS total_races,
                AVG(last_three_furlong ) AS avg_last_three_furlong_rate,
                COUNT(*) AS total_races
            FROM
                nar_race_results
            WHERE
                ba = %s AND
                distance = %s AND
                ground_condition = %s AND
                rule = %s AND
                f_name = %s
            GROUP BY
                f_name;
            """

            # クエリの実行
            cur.execute(query, (ba, distance, ground_condition, rule, f_name))

            # 結果を取得
            results = cur.fetchall()

            # 接続を閉じる
            cur.close()
            conn.close()

            return results
        
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    def get_mf_name_stats(self, ba, distance, ground_condition, rule, mf_name):
        try:
            # PostgreSQLデータベースへの接続
            conn = psycopg2.connect(
                dbname="chessdb",
                user="root",
                password="secret",
                host="192.168.56.18",
                port="5432"
            )
            cur = conn.cursor()

            # SQLクエリ
            query = """
            SELECT
                AVG(position) AS average_position,
                COUNT(*) AS total_races,
                AVG(corner_position_rate) AS avg_corner_position_rate, 
                COUNT(*) AS total_races,
                AVG(last_three_furlong ) AS avg_last_three_furlong_rate,
                COUNT(*) AS total_races
            FROM
                nar_race_results
            WHERE
                ba = %s AND
                distance = %s AND
                ground_condition = %s AND
                rule = %s AND
                mf_name = %s
            GROUP BY
                mf_name;
            """

            # クエリの実行
            cur.execute(query, (ba, distance, ground_condition, rule, mf_name))

            # 結果を取得
            results = cur.fetchall()

            # 接続を閉じる
            cur.close()
            conn.close()

            return results
        
        except Exception as e:
            print(f"Error: {e}")
            return None

    def get_pre_race_interval_week_stats(self, ba, distance, ground_condition, rule, pre_race_interval_week):
        try:
            # PostgreSQLデータベースへの接続
            conn = psycopg2.connect(
                dbname="chessdb",
                user="root",
                password="secret",
                host="192.168.56.18",
                port="5432"
            )
            cur = conn.cursor()

            # SQLクエリ
            query = """
            SELECT
                AVG(position) AS average_position,
                COUNT(*) AS total_races,
                AVG(corner_position_rate) AS avg_corner_position_rate, 
                COUNT(*) AS total_races,
                AVG(last_three_furlong ) AS avg_last_three_furlong_rate,
                COUNT(*) AS total_races
            FROM
                nar_race_results
            WHERE
                ba = %s AND
                distance = %s AND
                ground_condition = %s AND
                rule = %s AND
                pre_race_interval_week = %s
            GROUP BY
                pre_race_interval_week;
            """

            # クエリの実行
            cur.execute(query, (ba, distance, ground_condition, rule, pre_race_interval_week))

            # 結果を取得
            results = cur.fetchall()

            # 接続を閉じる
            cur.close()
            conn.close()

            return results
        
        except Exception as e:
            print(f"Error: {e}")
            return None