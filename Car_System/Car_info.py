import signal

import pigpio

"""
車の情報を管理するモジュール.
コメントの書き方は下記を参考にした.
https://qiita.com/simonritchie/items/49e0813508cad4876b5a
https://qiita.com/taka-kawa/items/673716d77795c937d422

"""


class Car_info:
    """
    車の情報を取得, 管理するクラス
    """

    speed_t_now = 0
    speed_t_last = 0
    tacho_t_now = 0
    tacho_t_last = 0
    # 車速及び回転数計のパルス周期測定に利用する変数

    Car_Speed = 0
    Car_tacho = 0
    # 車速及び回転数の変数

    def __init__(
        self, pi, SPEED_PULS_INPUT=6, TACHO_PULS_INPUT=7, TIRE_circumference=0.2
    ):
        """
        初期化処理.

        Parameters
        ----------
        pi : class
            外部でインスタンス化したpigpio.piのクラスオブジェクトを代入する変数.
        SPEED_PULS_INPUT : int
            車速パルス信号を入力するピン番号を指定する変数.
        TACHO_PULS_INPUT : int
            エンジン回転数計のパルス信号を入力するピン番号を指定する変数.
        TIRE_circumference : float
            タイヤの円周. 単位はメートル.
        """
        self.pi = pi
        self.SPEED_PULS_INPUT = SPEED_PULS_INPUT
        self.TACHO_PULS_INPUT = TACHO_PULS_INPUT
        self.TIRE_circumference = TIRE_circumference

        self.Back_Gear_Flag = 0
        # 各種フラグ

        pi.callback(SPEED_PULS_INPUT, pigpio.RISING_EDGE, self.SpeedCallBack)
        pi.callback(TACHO_PULS_INPUT, pigpio.RISING_EDGE, self.TachoCallBack)
        # callback_backgear = pi.callback(
        #    SPEED_PULS_INPUT, pigpio.EITHER_EDGE, self.BackGearCallBack
        # )
        signal.signal(signal.SIGALRM, self.poring)
        signal.setitimer(signal.ITIMER_REAL, 1, 1)

        # def CallBack_Set(self, Back_Gear_CBF):
        """
        バックギアに入れたときに実行されるコールバック関数を定義する関数

        Parameters
        ----------
        Back_Gear_CBF : function
            バックギアに入れたときコールバックされる関数を代入する変数
        """
        # self.Back_Gear_CBF = Back_Gear_CBF

    def SpeedCallBack(self, gpio, level, tick):
        """
        車速信号パルスの立ち上がりエッジにより呼び出されるコールバック関数. 割り込み用関数

        Parameters
        ----------
        gpio : ?
            未検証
        level : int
            立ち上がりエッジか立ち下がりエッジかを検出するための変数
        tick : float?(未検証)
            コールバック関数が呼び出されたときのタイマーの値を取得するための変数
        """

        self.speed_t_now = tick
        if self.speed_t_now >= self.speed_t_last:  # if wrapped 32bit value,
            timepassed = self.speed_t_now - self.speed_t_last
        else:
            timepassed = self.speed_t_now + (0xFFFFFFFF + 1 - self.speed_t_last)

        # microseconds to seconds, per_second to per_hour
        self.Car_Speed = (self.TIRE_circumference / (timepassed / 1000000)) * 3.6
        self.speed_t_last = self.speed_t_now

    def TachoCallBack(self, gpio, level, tick):
        """
        エンジン回転パルスの立ち上がりエッジにより呼び出されるコールバック関数. 割り込み用関数

        Parameters
        ----------
        gpio : ?
            未検証
        level : int
            立ち上がりエッジか立ち下がりエッジかを検出するための変数
        tick : float?(未検証)
            コールバック関数が呼び出されたときのタイマーの値を取得するための変数
        """

        self.tacho_t_now = tick
        if self.tacho_t_now >= self.tacho_t_last:  # if wrapped 32bit value,
            timepassed = self.tacho_t_now - self.tacho_t_last
        else:
            timepassed = self.tacho_t_now + (0xFFFFFFFF + 1 - self.tacho_t_last)

        # microseconds to seconds, per_second to per_hour
        self.Car_tacho = (1 / (timepassed / 1000000)) * 60
        self.tacho_t_last = self.tacho_t_now

    # def BackGearCallBack(self, gpio, level, tick):
    #    self.Back_Gear_Flag = level
    #    self.Back_Gear_CBF()

    def UndifinedCallBack():
        pass

    def poring():
        pass
