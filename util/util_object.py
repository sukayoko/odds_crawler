# util/util_object.py
from datetime import datetime

class RaceInfoObj:

    date : str
    weather : str
    ground_condition : str
    rule : str

    def __init__():
        pass

class HorseInfoObj:

    umaban : int
    horse_name : str
    jokey_name : str
    sex : str
    age : int
    birth_date : str
    hutan : str
    trainer : str
    owner : str
    farm : str
    weight : int
    f_name : str
    ff_name : str
    mf_name : str


    def __init__():
        pass

class NarRaceResultObj:
    date: datetime #開催日
    ba : str # 場
    race_num: int #レース番号
    distance: int # 距離
    weather: str # 天候
    ground_condition: str # 馬場状態
    rule : str # 条件

    horse_name: str # 馬名
    position: int   #着順
    umaban: int     #馬番
    age : int # 年齢
    sex : str # 性別
    birthday: str # 誕生日(年は除く)
    f_name: str #父親の名前
    ff_name: str # 父父の名前
    mf_name: str # 母父の名前
    farm: str # 生産牧場
    affiliation: str # 所属
    jokey_name : str # ジョッキー
    trainer_name : str # 調教師
    owner_name : str # 馬主
    additional_weight : float # 負担重量
    weight : float # バ体重
    record : int # 走破時間 (ミリ秒に変換)
    last_three_furlong : float # 上がり3ハロン
    popularity : int # 人気度

    corner_position_rate : int # それぞれのコーナでの位置の合計　低いほど前目にいたということ
    rounded_weight : float # 丸め体重
    pre_race_interval_week : int = 999 # 前走間隔(週)

    def __init__(self):
        pass
    
    def __str__(self):
        return f"{self.date},{self.ba},{self.race_num},{self.distance}, {self.weather}, {self.ground_condition},{self.rule},{self.horse_name},\
            {self.position},{self.umaban},{self.age},{self.sex},{self.birthday},{self.f_name},{self.ff_name},{self.mf_name},{self.farm},\
            {self.affiliation},{self.jokey_name},{self.trainer_name},{self.owner_name},{self.additional_weight},{self.weight}, {self.record},\
            {self.last_three_furlong},{self.popularity}, {self.corner_position_rate},{self.rounded_weight},{self.pre_race_interval_week}"
    

class RaceStatObj:

    sex_idx : float
    sex_total : int
    age_idx : float
    age_total : int
    birth_idx : float
    birth_total : int
    owner_idx : float
    owner_total : int
    farm_idx : float
    farm_total : int
    weight_idx : float
    weight_total : int
    jokey_idx : float
    jokey_total : int
    trainer_idx : float
    trainer_total : int
    f_idx : float
    f_total : int
    ff_idx : float
    ff_total : int
    mf_idx : float
    mf_total : int
    pre_race_idx : float
    pre_race_total : int


    def __init__(self):
        pass