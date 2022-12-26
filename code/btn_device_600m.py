import osTimer
from machine import Pin, KeyPad, ExtInt
from misc import PowerKey, Power
from usr.common import Abstract
from usr import EventMesh


class BtnDevice(Abstract):
    """物理按键类,3*2的矩阵键盘加pwk"""

    def __init__(self):
        self.__keypad = KeyPad(3, 2)
        self.__pk = PowerKey()
        self.__longpress_flag = 0
        self.__long_timer = osTimer()
        self.__pwk_timer = osTimer()
        self.__ok_btn_timer = osTimer()
        self.__up_btn_timer = osTimer()
        self.__down_btn_timer = osTimer()
        self.__up_longPress_flag = False
        self.__down_longPress_flag = False
        self.__PowerDownTimeOut = 2000
        self.group_count = 0
        self.group_cur = 0
        self.member_count = 0
        self.member_cur = 0

    def post_processor_after_instantiation(self):
        self.__keypad.init()
        self.__keypad.set_callback(self.__key_cb)
        self.__pk.powerKeyEventRegister(self.__pwk_callback)
        self.ej_ptt = ExtInt(ExtInt.GPIO19, ExtInt.IRQ_RISING_FALLING, ExtInt.PULL_PD, self.ej_ptt_cb)
        self.ej_ptt.enable()

    def ej_ptt_cb(self, ext_info):
        if ext_info[1]:
            self.__speak_press_handle()
        else:
            self.__speak_release_handle()

    def keypad_tone(self):
        if not EventMesh.publish("get_poc_keypad_tone") and EventMesh.publish("get_speaker_state") == 1:
            EventMesh.publish("audio_tone")

    def __key_cb(self, key_list):
        """矩阵键盘回调函数"""
        self.__key_event_manage(key_list)

    def __key_event_manage(self, event):
        if event[0] == 1 and event[1] == 0 and event[2] == 0:  # ok_btn按下
            self.keypad_tone()
            self.__ok_long_press_handle()
        elif event[0] == 0 and event[1] == 1 and event[2] == 0:  # sleep_btn抬起
            self.keypad_tone()
            self.__sleep_press_handle()
        elif event[0] == 0 and event[1] == 0 and event[2] == 0:  # ok_btn抬起
            self.__ok_press_handle()
        elif event[0] == 0 and event[1] == 1 and event[2] == 1:  # up/vol+抬起
            self.__up_press_handle()
        elif event[0] == 1 and event[1] == 1 and event[2] == 1:  # up/vol+按下
            self.keypad_tone()
            self.__up_long_press_handle()
        elif event[0] == 0 and event[1] == 0 and event[2] == 1:  # down/vol-抬起
            self.__down_press_handle()
        elif event[0] == 1 and event[1] == 0 and event[2] == 1:  # down/vol-长按
            self.keypad_tone()
            self.__down_long_press_handle()
        elif event[0] == 1 and event[1] == 2 and event[2] == 1:  # ptt按下
            self.__speak_press_handle()
        elif event[0] == 0 and event[1] == 2 and event[2] == 1:  # ptt抬起
            self.__speak_release_handle()

    def __ok_longPress_handle(self, args):
        """ok 长按锁键"""
        EventMesh.publish("btn_ok_long")

    def __longPress_handle(self, args):
        EventMesh.publish("btn_ptt_long")

    def __down_longPress_handle(self, args):
        self.__down_longPress_flag = True
        EventMesh.publish("btn_down_long")

    def __sleep_press_handle(self):
        '''
        息屏键处理方法,发送息屏事件
        '''
        EventMesh.publish("btn_sleep")

    def __ok_press_handle(self):
        '''
        KEY1:联动屏幕左下角或确认键
        '''
        self.__ok_btn_timer.stop()
        EventMesh.publish("btn_ok_on")

    def __ok_long_press_handle(self):
        '''
        KEY1:联动屏幕左下角或确认键
        '''
        EventMesh.publish("btn_ok_off")
        self.__ok_btn_timer.start(5000, 0, self.__ok_longPress_handle)

    def __pwk_long_press_cb(self, *args):
        '''KEY2:联动屏幕右下角或返回键长按关机'''
        EventMesh.publish("btn_back_long")

    def __pwk_callback(self, status):
        '''
        KEY2:联动屏幕右下角或返回键
        '''
        if status == 1:
            self.__pwk_timer.start(self.__PowerDownTimeOut, 0, self.__pwk_long_press_cb)
        elif status == 0:
            self.__pwk_timer.stop()
            EventMesh.publish("btn_back")

    def __down_press_handle(self):
        '''
        键盘S4：音量-或向右选择或向下选择 抬起
        '''
        # 主界面按下，音量-
        self.__down_btn_timer.stop()
        if not self.__down_longPress_flag:
            EventMesh.publish("btn_down_on")
        self.__down_longPress_flag = False

    def __down_long_press_handle(self):
        '''
        键盘S4：音量-长按 按下
        '''
        # 主界面按下，音量-
        self.__down_btn_timer.stop()
        self.__down_btn_timer.start(3000, 0, self.__down_longPress_handle)

    def __up_press_handle(self):
        """
        音量+或向左选择或向上选择按键回调
        """
        self.__up_btn_timer.stop()
        if not self.__up_longPress_flag:
            EventMesh.publish("btn_up")
        self.__up_longPress_flag = False

    def __up_long_press_handle(self):
        '''
        up长按处理
        '''
        self.__up_btn_timer.stop()
        self.__up_btn_timer.start(3000, 0, self.__up_longPress_handle)

    def __up_longPress_handle(self, *args):
        self.__up_longPress_flag = True
        EventMesh.publish("btn_up_long_press")

    def __speak_release_handle(self, *args):
        """
        群呼按键长按松开回调函数
        结束群呼
        """
        self.__long_timer.stop()
        EventMesh.publish("btn_ptt_off")

    def __speak_press_handle(self, *args):
        """
        群呼按键长按按下回调函数
        长按300ms以上算长按,否则算误按
        """
        EventMesh.publish("btn_ptt_on")
        self.__long_timer.start(100, 0, self.__longPress_handle)

    def start(self):
        self.post_processor_after_instantiation()
