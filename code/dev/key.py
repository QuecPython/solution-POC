import osTimer
import encoder
from machine import ExtInt, Pin
from misc import PowerKey, Power

try:
    from common import EventMap
except:
    from usr.common import EventMap


class BtnEnum:
    PTT_PRESS = "PTT_PRESS"
    PTT_LONG = "PTT_LONG"
    PTT_RELEASE = "PTT_RELEASE"
    MENU_PRESS = "MENU_PRESS"
    MENU_LONG = "MENU_LONG"
    MENU_RELEASE = "MENU_RELEASE"
    OK_PRESS = "OK_PRESS"
    OK_LONG = "OK_LONG"
    OK_RELEASE = "OK_RELEASE"
    UP_PRESS = "UP_PRESS"
    UP_LONG = "UP_LONG"
    UP_RELEASE = "UP_RELEASE"
    DOWN_PRESS = "DOWN_PRESS"
    DOWN_LONG = "DOWN_LONG"
    DOWN_RELEASE = "DOWN_RELEASE"
    BACK_PRESS = "BACK_PRESS"
    BACK_LONG = "BACK_LONG"
    BACK_RELEASE = "BACK_RELEASE"
    ENCODER_LEFT = "ENCODER_LEFT"
    ENCODER_RIGHT = "ENCODER_RIGHT"
    PWK_PRESS = "PWK_PRESS"
    PWK_LONG = "PWK_LONG"
    PWK_RELEASE = "PWK_RELEASE"


class PTT(object):
    def __init__(self, callback):
        self.flag = False
        self.t = osTimer()
        self.key = ExtInt(ExtInt.GPIO5, ExtInt.IRQ_RISING_FALLING, ExtInt.PULL_PU, self.up)
        self.callback = callback
        self.key.enable()

    def reset(self, *args):
        self.flag = False
        self.callback(self.key.read_level())
        self.key.enable()

    def up(self, *args):
        if not self.flag:
            self.flag = True
            self.t.stop()
            self.t.start(20, 0, self.reset)
        else:
            self.key.disable()


class BTN(object):
    def __init__(self, press_meta, release_meta, long_meta, long_time=2000, disable=False):
        self.press_meta = press_meta
        self.release_meta = release_meta
        self.long_meta = long_meta
        self.long_time = long_time
        self.long_flag = False
        self.disable = disable
        self.timer = osTimer()

    def press(self):
        if not self.disable:
            self.timer.stop()
            self.timer.start(self.long_time, 0, self.long)
        EventMap.send(self.press_meta)
        # print("press {}".format(self.press_meta))

    def long(self, *args):
        self.long_flag = True
        EventMap.send(self.long_meta)
        # print("long {}".format(self.long_meta))

    def release(self):
        if self.disable:
            EventMap.send(self.release_meta)
        else:
            self.timer.stop()
            if not self.long_flag:
                EventMap.send(self.release_meta)
            self.long_flag = False


class KeyManger(object):
    def __init__(self):
        self.ptt = PTT(self.ptt_callback)
        self.menu = BTN(BtnEnum.MENU_PRESS, BtnEnum.MENU_RELEASE, BtnEnum.MENU_LONG)
        self.up = BTN(BtnEnum.UP_PRESS, BtnEnum.UP_RELEASE, BtnEnum.UP_LONG)
        self.down = BTN(BtnEnum.DOWN_PRESS, BtnEnum.DOWN_RELEASE, BtnEnum.DOWN_LONG)
        self.SK2 = BTN(BtnEnum.BACK_PRESS, BtnEnum.BACK_RELEASE, BtnEnum.BACK_LONG)
        self.SK1 = BTN(BtnEnum.OK_PRESS, BtnEnum.OK_RELEASE, BtnEnum.OK_LONG)
        self.pwk = BTN(BtnEnum.PWK_PRESS, BtnEnum.PWK_RELEASE, BtnEnum.PWK_LONG)
        self.__menu_key = ExtInt(ExtInt.GPIO22, ExtInt.IRQ_RISING_FALLING, ExtInt.PULL_PU, self.key_callback)
        self.__up_key = ExtInt(ExtInt.GPIO10, ExtInt.IRQ_RISING_FALLING, ExtInt.PULL_PU, self.key_callback)
        self.__down_key = ExtInt(ExtInt.GPIO21, ExtInt.IRQ_RISING_FALLING, ExtInt.PULL_PU, self.key_callback)
        self.__sk2_key = ExtInt(ExtInt.GPIO4, ExtInt.IRQ_RISING_FALLING, ExtInt.PULL_PU, self.key_callback)
        self.__sk1_key = ExtInt(ExtInt.GPIO3, ExtInt.IRQ_RISING_FALLING, ExtInt.PULL_PU, self.key_callback)
        self.__menu_key.enable()
        self.__up_key.enable()
        self.__down_key.enable()
        self.__sk2_key.enable()
        self.__sk1_key.enable()
        self.power_key = PowerKey()
        self.power_key.powerKeyEventRegister(self.pwk_callback)
        self.encoder = encoder(Pin.GPIO12, Pin.GPIO11)
        self.encoder.set_callback(self.encoder_callback)

    def ptt_callback(self, level):
        if not level:
            EventMap.send(BtnEnum.PTT_PRESS)
            # print("PTT Press")
        else:
            EventMap.send(BtnEnum.PTT_RELEASE)
            # print("PTT Release")
            

    def key_callback(self, args):
        # print("args {}".format(args))
        if args[0] == ExtInt.GPIO22:
            if not self.__menu_key.read_level():
                self.menu.press()
            else:
                self.menu.release()
        elif args[0] == ExtInt.GPIO10:
            if not self.__up_key.read_level():
                self.up.press()
            else:
                self.up.release()
        elif args[0] == ExtInt.GPIO21:
            if not self.__down_key.read_level():
                self.down.press()
            else:
                self.down.release()
        elif args[0] == ExtInt.GPIO4:
            if not self.__sk2_key.read_level():
                self.SK2.press()
            else:
                self.SK2.release()
        elif args[0] == ExtInt.GPIO3:
            if not self.__sk1_key.read_level():
                self.SK1.press()
            else:
                self.SK1.release()

    
    def pwk_callback(self, args):
        if args == 0:
            self.pwk.release()
            # print('powerkey release.')
        elif args == 1:
            self.pwk.press()
            # print('powerkey press.')

    def encoder_callback(self, args):
        # This method can be used to handle encoder events if needed
        print("Encoder event:", args)
        if args == 2:
            EventMap.send(BtnEnum.ENCODER_LEFT)
        elif args == 1:
            EventMap.send(BtnEnum.ENCODER_RIGHT)



if __name__ == "__main__":
    key_manager = KeyManger()
