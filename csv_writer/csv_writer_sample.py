import csv

# 構造体の定義
class Struct:
    def __init__(self, field1, field2, field3):
        self.field1 = field1
        self.field2 = field2
        self.field3 = field3

def main():
    # ここにメインの処理を記述する
    # サンプルのデータ
    data_list = [
        Struct("value1", "value2", "value3"),
        Struct("value4", "value5", "value6"),
        Struct("value7", "value8", "value12")
    ]

    # CSVファイルにデータを書き込む (追記ではなく上書き)
    with open('output.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        
        # ヘッダー行を書き込む（フィールド名）
        writer.writerow(['Field1', 'Field2', 'Field3'])
        
        # 各構造体のフィールド値を一行ずつ書き込む
        for struct in data_list:
            writer.writerow([struct.field1, struct.field2, struct.field3])

        pass
    

# スクリプトが直接実行された場合のみ
if __name__ == "__main__":
    main()
