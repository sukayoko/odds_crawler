from psql import PostgresClient

def main():
    psql_client = PostgresClient()
    result = psql_client.get_jockey_stats( "大井", 1600, "良", "一般", "石川駿aa")

    if (result) :

        print(result)
        print(result[0])
        print(result[0][0])    
        print(result[0][1])        
    else :
        print("s")

# スクリプトが直接実行された場合のみ
if __name__ == "__main__":
    main()