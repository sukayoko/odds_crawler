# 全然未完成

from cryptography.fernet import Fernet
import configparser
from const import *


# Selenium クラス
class LocalConfig:
    # 設定ファイルの構造体
    config = configparser.ConfigParser()
    conf_path = "config.ini"

    def test(self):
        # 設定ファイルから値を読み込み、必要に応じて一部を暗号化
        normal_setting = self.config['Settings']['normal_setting']
        encrypted_setting_plain = self.config['Settings']['encrypted_setting']

        # 一部の設定だけを暗号化
        key = self.generate_key()
        print(key)
        encrypted_setting = self.encrypt_value(key, encrypted_setting_plain)

        print(f'Normal Setting: {normal_setting}')
        print(f'Encrypted Setting: {encrypted_setting}')

        # 復号する場合
        decrypted_setting = self.decrypt_value(key, encrypted_setting)
        print(f'Decrypted Setting: {decrypted_setting}')

    # コンストラクタ
    def __init__(self, path):
        # 設定ファイル読み込み
        self.conf_path = path
        self.config.read(self.conf_path)
        

    def __del__(self):
        pass


    

    # configの読み込み
    def checkCfg(self):

        
        return
    


    # configの書き込み
    ## うまくすべてが書き込めない？
    def write(self):
        with open(self.conf_path, 'w') as configfile:
            self.config.write(configfile)
        pass

    # 指定のカテゴリのキーを取得
    # 引数は enumに固定した方がいいかも
    def getConfigValue(self, category, key):

        try :
            val = self.config[category][key]
            return val
        except KeyError:
            print("failed to get config. category:" + category + ", key:" + key)
            return None
    
    # 指定のカテゴリのキーを設定
    # 引数は enumに固定した方がいいかも
    def setConfigValue(self, category, key, val):
        try :
            self.config[category][key] = val
            return val
        except KeyError:
            print("failed to set config. category:" + category + ", key:" + key)
            return None

    def generate_key():
        # return Fernet.generate_key()

        # とりあえず暗号キーを固定  Fernet key must be 32 url-safe base64-encoded bytes.　らしい
        return CONFIG_KEY.encode('utf-8')

    # 暗号化
    def encrypt_value(self, value):
        cipher_suite = Fernet(CONFIG_KEY)
        encrypted_value = cipher_suite.encrypt(value.encode('utf-8'))
        return encrypted_value


    # 復号化
    def decrypt_value(self, encrypted_value):
        cipher_suite = Fernet(CONFIG_KEY)
        decrypted_value = cipher_suite.decrypt(encrypted_value).decode('utf-8')
        return decrypted_value
    