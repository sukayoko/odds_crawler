import csv

# influx db への登録用 クラス
class CsvWriter:

    def __init__(self, file_name):
        self.file_name = file_name
        self.file = open(self.file_name, 'w', newline='', encoding='utf-8')
        self.writer = csv.writer(self.file)        

    def __del__(self):
        self.file.close()

    def close(self):
        self.__del__()

    def write_row(self, row):
        if isinstance(row, str):
            self.writer.writerow([row])
        else:
            self.writer.writerow(row)