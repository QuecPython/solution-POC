import _thread

import utime
import audio
import osTimer
import ql_fs
import sim
import net
import modem
import pm
import poc
import lvgl
import dataCall
import checkNet
from misc import Power, ADC
from machine import Pin, ExtInt
from usr import EventMesh
from usr.common import Lock
from usr.common import Abstract
from usr.common import LogAdapter
from misc import USB

BATTERY_OCV_TABLE = {
    "nix_coy_mnzo2": {
        55: {
            4152: 100, 4083: 95, 4023: 90, 3967: 85, 3915: 80, 3864: 75, 3816: 70, 3773: 65, 3737: 60, 3685: 55,
            3656: 50, 3638: 45, 3625: 40, 3612: 35, 3596: 30, 3564: 25, 3534: 20, 3492: 15, 3457: 10, 3410: 5, 3380: 0,
        },
        20: {
            4143: 100, 4079: 95, 4023: 90, 3972: 85, 3923: 80, 3876: 75, 3831: 70, 3790: 65, 3754: 60, 3720: 55,
            3680: 50, 3652: 45, 3634: 40, 3621: 35, 3608: 30, 3595: 25, 3579: 20, 3548: 15, 3511: 10, 3468: 5, 3430: 0,
        },
        0: {
            4147: 100, 4089: 95, 4038: 90, 3990: 85, 3944: 80, 3899: 75, 3853: 70, 3811: 65, 3774: 60, 3741: 55,
            3708: 50, 3675: 45, 3651: 40, 3633: 35, 3620: 30, 3608: 25, 3597: 20, 3585: 15, 3571: 10, 3550: 5, 3500: 0,
        },
    },
}


class Battery(object):
    """This class is for battery info.

    This class can get battery voltage and energy.
    if adc_args is not None, use cbc to read battery

    adc_args: (adc_num, adc_period, factor)

        adc_num: ADC channel num
        adc_period: Cyclic read ADC cycle period
        factor: calculation coefficient
    """

    def __init__(self, adc_args=None, chrg_gpion=None, stdby_gpion=None):
        self.__energy = 100
        self.__temp = 55

        # ADC params
        self.__adc = None
        if adc_args:
            self.__adc_num, self.__adc_period, self.__factor = adc_args
            if not isinstance(self.__adc_num, int):
                raise TypeError("adc_args adc_num is not int number.")
            if not isinstance(self.__adc_period, int):
                raise TypeError("adc_args adc_period is not int number.")
            if not isinstance(self.__factor, float):
                raise TypeError("adc_args factor is not int float.")
            self.__adc = ADC()

        # Charge params
        self.__charge_callback = None
        self.__charge_status = None
        self.__chrg_gpion = chrg_gpion
        self.__stdby_gpion = stdby_gpion
        self.__chrg_gpio = None
        self.__stdby_gpio = None
        self.__chrg_exint = None
        self.__stdby_exint = None
        if self.__chrg_gpion is not None and self.__stdby_gpion is not None:
            self.__init_charge()

    def __chrg_callback(self, args):
        self.__update_charge_status()
        if self.__charge_callback is not None:
            self.__charge_callback(self.__charge_status)

    def __stdby_callback(self, args):
        self.__update_charge_status()
        if self.__charge_callback is not None:
            self.__charge_callback(self.__charge_status)

    def __update_charge_status(self):
        if self.__chrg_gpio.read() == 1 and self.__stdby_gpio.read() == 1:
            self.__charge_status = 0
        elif self.__chrg_gpio.read() == 0 and self.__stdby_gpio.read() == 1:
            self.__charge_status = 1
        elif self.__chrg_gpio.read() == 1 and self.__stdby_gpio.read() == 0:
            self.__charge_status = 2
        else:
            raise TypeError("CHRG and STDBY cannot be 0 at the same time!")

    def __init_charge(self):
        self.__chrg_gpio = Pin(self.__chrg_gpion, Pin.IN, Pin.PULL_DISABLE)
        self.__stdby_gpio = Pin(self.__stdby_gpion, Pin.IN, Pin.PULL_DISABLE)
        self.__chrg_exint = ExtInt(self.__chrg_gpion, ExtInt.IRQ_RISING_FALLING, ExtInt.PULL_PU, self.__chrg_callback)
        self.__stdby_exint = ExtInt(self.__stdby_gpion, ExtInt.IRQ_RISING_FALLING, ExtInt.PULL_PU,
                                    self.__stdby_callback)
        self.__chrg_exint.enable()
        self.__stdby_exint.enable()
        self.__update_charge_status()

    def __get_soc_from_dict(self, key, volt_arg):
        """Get battery energy from map"""
        if key in BATTERY_OCV_TABLE["nix_coy_mnzo2"]:
            volts = sorted(BATTERY_OCV_TABLE["nix_coy_mnzo2"][key].keys(), reverse=True)
            pre_volt = 0
            volt_not_under = 0  # Determine whether the voltage is lower than the minimum voltage value of soc.
            for volt in volts:
                if volt_arg > volt:
                    volt_not_under = 1
                    soc1 = BATTERY_OCV_TABLE["nix_coy_mnzo2"][key].get(volt, 0)
                    soc2 = BATTERY_OCV_TABLE["nix_coy_mnzo2"][key].get(pre_volt, 0)
                    break
                else:
                    pre_volt = volt
            if pre_volt == 0:  # Input Voltarg > Highest Voltarg
                return soc1
            elif volt_not_under == 0:
                return 0
            else:
                return soc2 - (soc2 - soc1) * (pre_volt - volt_arg) // (pre_volt - volt)

    def __get_soc(self, temp, volt_arg, bat_type="nix_coy_mnzo2"):
        """Get battery energy by temperature and voltage"""
        if bat_type == "nix_coy_mnzo2":
            if temp > 30:
                return self.__get_soc_from_dict(55, volt_arg)
            elif temp < 10:
                return self.__get_soc_from_dict(0, volt_arg)
            else:
                return self.__get_soc_from_dict(20, volt_arg)

    def __get_power_vbatt(self):
        return int(sum([Power.getVbatt() for i in range(100)]) / 100)

    def __get_adc_vbatt(self):
        self.__adc.open()
        utime.sleep_ms(self.__adc_period)
        adc_list = list()
        for i in range(self.__adc_period):
            adc_list.append(self.__adc.read(self.__adc_num))
            utime.sleep_ms(self.__adc_period)
        adc_list.remove(min(adc_list))
        adc_list.remove(max(adc_list))
        adc_value = int(sum(adc_list) / len(adc_list))
        self.__adc.close()
        vbatt_value = adc_value * (self.__factor + 1)
        return vbatt_value

    def set_temp(self, temp):
        """Set now temperature."""
        if isinstance(temp, int) or isinstance(temp, float):
            self.__temp = temp
            return True
        return False

    def get_voltage(self):
        """Get battery voltage"""
        if self.__adc is None:
            return self.__get_power_vbatt()
        else:
            return self.__get_adc_vbatt()

    def get_energy(self):
        """Get battery energy"""
        self.__energy = self.__get_soc(self.__temp, self.get_voltage())
        return self.__energy

    def set_charge_callback(self, charge_callback):
        if self.__chrg_gpion is not None and self.__stdby_gpion is not None:
            if callable(charge_callback):
                self.__charge_callback = charge_callback
                return True
        return False

    def get_charge_status(self):
        return self.__charge_status


class BatteryManager(Abstract):
    def __init__(self):
        """???????????????"""
        self.battery = Battery()
        self.low_battery = False

    def post_processor_after_instantiation(self):
        """?????????????????????????????? EventMesh???"""
        EventMesh.subscribe("get_battery", self.get_battery)

    def get_battery(self, event=None, msg=None):
        battery = self.battery.get_energy()
        return battery


################################################################
#                   config manager ??????
# description: ??????????????????
# auth:pawn
################################################################
class ConfigStoreManager(Abstract):
    def __init__(self):
        self.file_name = "/usr/conf_store.json"
        self.lock = Lock()
        self.map = dict(
            media_vol=11,
            lcd_sleep_time_mode=30,
            quit_call_time=30,
            low_power_mode=30,
            platform=0,
            sim_mode=1,
            ptt_hint_tone=0,
            keypad_tone=0
        )

    def post_processor_after_instantiation(self):
        if ql_fs.path_exists(self.file_name):
            self.map = ql_fs.read_json(self.file_name)
        else:
            self.__store()
        EventMesh.subscribe("persistent_config_get", self.__read)
        EventMesh.subscribe("persistent_config_store", self.__store)

    def __read(self, event, msg):
        with self.lock:
            return self.map.get(msg)

    def __store(self, event=None, msg=None):
        if msg is None:
            msg = dict()
        with self.lock:
            self.map.update(msg)
            ql_fs.touch(self.file_name, self.map)


################################################################
#                   device manager ??????
# description: ??????????????????
# auth:pawn
################################################################
class DeviceInfoManager(Abstract):
    """
        ??????????????????
    """

    def __init__(self):
        self.__city = None
        self.__location = None
        self.timer_push_schedule = osTimer()
        self.usb = USB()
        self.battery_push_schedule = osTimer()
        self.check_battery_list = []
        self.__bat_num = 0
        self.usb.setCallback(self.usb_event_cb)
        self.log = LogAdapter(self.__class__.__name__)

    def post_processor_after_instantiation(self):
        """?????????????????????????????? EventMesh???"""
        EventMesh.subscribe("screen_get_ope", self.get_device_ope)
        EventMesh.subscribe("screen_get_sig", self.get_signal)
        EventMesh.subscribe("screen_get_time", self.get_time)
        EventMesh.subscribe("about_get_imei", self.get_imei)
        EventMesh.subscribe("about_get_iccid", self.get_ic_cid)
        EventMesh.subscribe("about_get_phonenum", self.get_phone_num)
        EventMesh.subscribe("screen_get_battery", self.get_battery)
        EventMesh.subscribe("get_poc_fw_version", self.get_device_fw_version)
        EventMesh.subscribe("get_poc_version", self.get_poc_version)
        EventMesh.subscribe("get_standby_time", self.get_standby_time)
        EventMesh.subscribe("sim_slot_get", self.sim_slot_get)
        EventMesh.subscribe("sim_slot_switch", self.sim_slot_switch)
        self.timer_push_schedule.start(20000, 1, self.publish_event)
        self.battery_push_schedule.start(3000, 1, self.__check_battery)
        self.log.debug("post_processor_after_instantiation finished")

    def __check_battery(self, *args):
        if EventMesh.publish("get_battery"):
            self.check_battery_list.append(EventMesh.publish("get_battery"))
            if len(self.check_battery_list) > 2:
                check_battery_list = self.check_battery_list.copy()
                check_battery_list.remove(min(self.check_battery_list))
                check_battery_list.remove(max(self.check_battery_list))
                _bat = sum(check_battery_list) / len(check_battery_list)
                if len(self.check_battery_list) > 20:
                    self.check_battery_list = self.check_battery_list[1:]
                self.__bat_num = _bat
            else:
                return EventMesh.publish("get_battery")

    def publish_event(self, *args, **kwargs):
        """
        ??????????????????
        :param args:
        :param kwargs:
        :return:
        """
        EventMesh.publish("time", self.get_time())
        EventMesh.publish("battery", self.get_battery())
        EventMesh.publish("signal", self.get_signal())

    def get_device_ope(self, event, msg):
        """
        ???????????????????????????
        :param event:
        :param msg:
        :return: ?????????
        """
        net_ope_map = {
            "UNICOM": "????????????",
            "CMCC": "????????????",
            "CT": "????????????"
        }
        """???????????????"""
        try:
            short_eons = net.operatorName()[1]
        except Exception:
            return "???"
        return net_ope_map.get(short_eons, None)

    def get_signal(self, event=None, msg=None):
        """
        ??????????????????
        :param event:
        :param msg:
        :return: int ??????
        """
        return net.csqQueryPoll()

    def get_time(self, event=None, msg=None):
        """
        ??????????????????
        :param event:
        :param msg:
        :return: HH:MM ??????
        """
        local_time = utime.localtime()
        date = "{0:02d}-{1:02d}-{2:02d}".format(local_time[0], local_time[1], local_time[2])
        time = "{0:02d}:{1:02d}".format(local_time[3], local_time[4])
        result = [date, time]
        return result

    def get_imei(self, event, msg):
        """
        ??????imsi???s??????
        :param event:
        :param msg:
        :return: str imsi
        """
        return modem.getDevImei()

    def get_ic_cid(self, event, msg):
        """
        ??????ic cid??????
        :param event:
        :param msg:
        :return: str ic cid
        """
        return sim.getIccid()

    def get_phone_num(self, event, msg):
        """
        ????????????????????????
        :param event:
        :param msg:
        :return: str number
        """
        return sim.getPhoneNumber()

    def get_battery(self, event=None, msg=None):
        """
        ??????????????????,???????????????
        :param event:
        :param msg:
        :return:
        """
        battery_level = int(self.__bat_num / 20)
        if battery_level == 5:
            battery_level = 4
        if battery_level == 0:
            battery_level = 1
        if self.get_usb_state():
            img_path = 'B:/static/charge_battery_' + str(battery_level) + '.png'
        else:
            img_path = 'B:/static/battery_' + str(battery_level) + '.png'
        return img_path

    def get_device_fw_version(self, *args):
        '''
        ???????????????????????????
        '''
        fw_version = modem.getDevFwVersion()
        if isinstance(fw_version, str):
            return fw_version
        return "--"

    def get_poc_version(self, *args):
        '''
        ??????POC???????????????
        '''
        return poc.get_version()

    def get_standby_time(self, *args):
        '''
        ????????????????????????????????????
        '''
        time_msg = utime.time()
        d = int(
            time_msg / 86400)  # The int call removes the decimals.  Conveniently, it always rounds down.  int(2.9) returns 2 instead of 3, for example.
        time_msg -= (
                d * 86400)  # This updates the value of x to show that the already counted seconds won't be double counted or anything.
        h = int(time_msg / 3600)
        time_msg -= (h * 3600)
        m = int(time_msg / 60)
        time_msg -= (m * 60)
        s = time_msg
        result = "{}???{}??????{}???".format(d, h, m)
        return result

    def sim_slot_get(self, topic=None, msg=None):
        return sim.getCurSimid()

    def sim_slot_switch(self, topic=None, slot=None):
        """
        sim ????????????
        :param topic:
        :param slot:
        :return: ??????sim?????????  0 ????????????, 1 ????????????, -1 ????????????
        """
        if self.sim_slot_get() == slot:
            return 1
        else:
            return sim.switchCard(slot)

    def usb_event_cb(self, state):
        # with open("/usr/usb.txt", "a+", encoding="utf8")as f:
        #     if state:
        #         f.write("1")
        #     else:
        #         f.write("0")
        EventMesh.publish("battery", self.get_battery())

    def get_usb_state(self):
        state = self.usb.getStatus()
        if state == -1:
            state = 0
        return state


class LedManage(Abstract):
    """This class is for control LED"""

    def __init__(self):
        """LED object init"""
        self.__led_timer = osTimer()
        self.__red_led = Pin(Pin.GPIO11, Pin.OUT, Pin.PULL_DISABLE, 0)
        self.__blue_led = Pin(Pin.GPIO12, Pin.OUT, Pin.PULL_DISABLE, 0)
        self.__last_task = None
        self.__last_task_name = None
        self.lock = Lock()
        self.__led_mode = {
            "heartbeat_led": [self.heartbeat_indicator_light, 5000, 1],
            "low_heartbeat_led": [self.low_heartbeat_indicator_light, 1200, 1],
            "net_error": [self.net_state_light, 2000, 1]
        }

    def post_processor_after_instantiation(self):
        """?????????????????????????????? EventMesh???"""
        EventMesh.subscribe("start_led_timer", self.start_flicker)
        EventMesh.subscribe("stop_led_timer", self.stop_flicker)
        EventMesh.subscribe("reset_led_timer", self.reset_led_timer)
        EventMesh.subscribe("ptt_led", self.press_ptt_light)
        EventMesh.subscribe("ptt_receive_led", self.receive_ptt_light)
        self.start_flicker(data="heartbeat_led")

    def red_on(self):
        """Set led on"""
        self.__red_led.write(1)

    def red_off(self):
        """Set led off"""
        self.__red_led.write(0)

    def blue_on(self):
        """Set led on"""
        self.__blue_led.write(1)

    def blue_off(self):
        """Set led off"""
        self.__blue_led.write(0)

    def _heartbeat_indicator_light(self, *args):
        self.blue_on()
        utime.sleep_ms(500)
        self.blue_off()

    def heartbeat_indicator_light(self, args):
        '''???????????????'''
        _thread.start_new_thread(self._heartbeat_indicator_light, ())

    def _low_heartbeat_indicator_light(self, *args):
        self.red_on()
        utime.sleep_ms(800)
        self.red_off()

    def low_heartbeat_indicator_light(self, args):
        '''?????? 3.4v ???????????????'''
        _thread.start_new_thread(self._low_heartbeat_indicator_light, ())

    def press_ptt_light(self, topic, data):
        '''??????PTT ?????????'''
        if data:
            # ptt??????
            self.stop_flicker()
            self.blue_off()
            self.red_on()
        else:
            # ptt??????
            self.red_off()
            self.start_flicker()

    def receive_ptt_light(self, topic, data):
        '''??????ptt???????????????'''
        if data:
            # ????????????
            self.stop_flicker()
            self.red_off()
            self.blue_on()
        else:
            # ????????????
            self.blue_off()
            self.start_flicker()

    def _net_state_light(self, *args):
        for i in range(0, 2):
            self.blue_on()
            utime.sleep_ms(300)
            self.blue_off()
            utime.sleep_ms(200)

    def net_state_light(self, args):
        '''SIM?????????????????????'''
        _thread.start_new_thread(self._net_state_light, ())

    def start_flicker(self, topic=None, data=None):
        """Start led flicker"""
        with self.lock:
            if data:
                mode_list = self.__led_mode.get(data)
                self.__last_task = mode_list
                self.__last_task_name = data
            elif self.__last_task:
                mode_list = self.__last_task
            else:
                return
            self.__led_timer.start(mode_list[1], mode_list[2], mode_list[0])

    def stop_flicker(self, topic=None, data=None):
        """Stop LED flicker"""
        with self.lock:
            self.__led_timer.stop()

    def reset_led_timer(self, topic=None, data=None):
        if data == 2:
            if EventMesh.publish("get_battery") > 5:
                led_task = "heartbeat_led"
            else:
                led_task = "low_heartbeat_led"
        else:
            led_task = "net_error"
        if self.__last_task_name != led_task:
            self.stop_flicker()
            self.start_flicker(topic, led_task)


class LowPowerManager(Abstract):
    class Mode:
        LOWER_POWER = 0
        ROUSE_LOWER_POWER = 1
        DEPTH_LOWER_POWER = 2

    def __init__(self):
        self.lpm_name = "lower_power"
        self.lpm = pm.create_wakelock(self.lpm_name, len(self.lpm_name))
        self.lower_power_state = 1
        self.lock = Lock()

    def post_processor_after_instantiation(self):
        EventMesh.subscribe("lower_power", self.lower_power)
        EventMesh.subscribe("get_lower_power_state", self.get_lower_power_state)
        pm.autosleep(1)
        self.rouse()

    def get_lower_power_state(self, event, msg):
        return self.lower_power_state

    def weak(self):
        """
        ?????????
        :return:
        """
        pm.autosleep(1)
        lvgl.autoSleep(1)

    def rouse(self):
        """
        ??????
        :return:
        """
        pm.autosleep(0)
        lvgl.autoSleep(0)

    def lower_power(self, event, mode):
        self.lower_power_state = mode
        if mode == self.Mode.LOWER_POWER:
            self.weak()
        elif mode == self.Mode.ROUSE_LOWER_POWER:
            self.rouse()
        elif mode == self.Mode.DEPTH_LOWER_POWER:
            Power.powerDown()


class MediaManager(Abstract):
    """
        ????????????
    """

    def __init__(self):
        utime.sleep(3)
        import audio
        # self.tts = audio.TTS(0)
        self.aud = audio.Audio(0)
        self.tts = audio.TTS(0)
        self.tts.setVolume(1)
        self.PA_Play_State = 0
        self.log = LogAdapter(self.__class__.__name__)
        self.mic_det = Pin(Pin.GPIO30, Pin.IN, Pin.PULL_DISABLE, 0)
        # self.aud.setSpeakerpaCallback(self.speaker_pa_callback)
        self.__p18 = Pin(Pin.GPIO18, Pin.OUT, Pin.PULL_DISABLE, 0)
        self.__p18.write(0)
        if self.mic_det.read():
            self.aud.set_pa(Pin.GPIO18, 4)
            self.mic_sel = Pin(Pin.GPIO20, Pin.OUT, Pin.PULL_DISABLE, 0)
        else:
            self.mic_sel = Pin(Pin.GPIO20, Pin.OUT, Pin.PULL_DISABLE, 1)
        self.ext_mic_det = ExtInt(ExtInt.GPIO30, ExtInt.IRQ_RISING_FALLING, ExtInt.PULL_PD, self.cb)
        self.ext_mic_det.enable()

    def speaker_pa_callback(self, para):
        if para == 1 and self.PA_Play_State == 1:
            print("speaker_pa_callback {} {}".format(para, self.PA_Play_State))
            self.__p18.write(0)
            self.PA_Play_State = 0

    def cb(self, ext_info):
        if ext_info[1]:
            EventMesh.publish("update_ej_img", 1)
            self.mic_sel.write(1)
            self.aud.set_pa(Pin.GPIO18, 0)
        else:
            EventMesh.publish("update_ej_img", 0)
            self.aud.set_pa(Pin.GPIO18, 4)
            self.mic_sel.write(0)

    def post_processor_after_instantiation(self):
        # from machine import Pin
        """????????????????????????"""
        EventMesh.subscribe("screen_vol_add", self.add_volume)
        EventMesh.subscribe("screen_vol_reduce", self.reduce_volume)
        EventMesh.subscribe("get_mic_det_state", self.get_mic_det_state)
        # EventMesh.subscribe("set_PA_Play_State", self.set_pa_play_state)
        # EventMesh.subscribe("get_PA_Play_State", self.get_pa_play_state)
        EventMesh.subscribe("audio_tone", self.aud_tone)
        poc.set_vol(1, 8)
        # self.aud.set_pa(Pin.GPIO18, 4)
        # ??????????????????????????????
        vol = EventMesh.publish("persistent_config_get", "media_vol")
        self.__set_volume(vol)

    def set_pa_play_state(self, event, msg):
        self.PA_Play_State = msg
        self.__p18.write(1 - msg)

    def get_pa_play_state(self, event, msg):
        return self.PA_Play_State

    def aud_tone(self, event, msg):
        self.aud.aud_tone_play(16, 100)

    def get_mic_det_state(self, event, msg):
        return self.mic_det.read()

    def __set_volume(self, vol):
        """????????????"""
        if vol != self.get_volume() and 0 <= vol <= 11:
            # self.aud.setVolume(vol)
            EventMesh.publish("persistent_config_store", {"media_vol": vol})
            print("vol - {} get_volume={}".format(vol, self.get_volume()))
            if vol == 0 and self.get_volume() == 1:
                print("?????????")
                self.aud.set_pa(Pin.GPIO18, 0)
            if vol == 1 and self.get_volume() == 0 and self.mic_det.read():
                print("??????")
                self.aud.set_pa(Pin.GPIO18, 4)
                print("????????????")
            self.aud.setVolume(vol)

    def get_volume(self):
        """????????????"""
        # return self.aud.getVolume()
        return self.aud.getVolume()

    def tts_play(self, event=None, msg=None):
        """??????tts????????????"""
        self.log.info("tts play -------------------")
        self.tts.play(*msg)

    def add_volume(self, event, msg):
        """????????????"""
        self.__set_volume(self.get_volume() + 1)
        return self.get_volume()

    def reduce_volume(self, event, msg):
        """????????????"""
        self.__set_volume(self.get_volume() - 1)
        return self.get_volume()


class NetManager(Abstract):
    THRESHOLD = 10

    def __init__(self):
        self.__data_call = dataCall
        self.__net = net
        self.check_net = checkNet.CheckNetwork("QuecPython_Helios_Framework", "this latest version")
        self.timer = osTimer()
        self.check_net_timeout = 100 * 1000
        self.error_count = 0
        self.__net_sign = "4G"
        self.log = LogAdapter(self.__class__.__name__)

    def post_processor_after_instantiation(self, *args, **kwargs):
        """
        ??????????????????
        :param args:
        :param kwargs:
        :return:
        """
        EventMesh.subscribe("set_net_check_time", self.set_keepalive)
        EventMesh.subscribe("publish_net_show", self.__net_cb)
        EventMesh.subscribe("set_net_show", self.__set_net)
        self.__data_call.setCallback(self.__datacall_cb)

    def __datacall_cb(self, args):
        pdp = args[0]
        nw_sta = args[1]
        if nw_sta == 1:
            state = 2
            print("*** network %d connected! ***" % pdp)
            EventMesh.publish('network_state', state)
        else:
            state = 3
            print("*** network %d not connected! ***" % pdp)
            EventMesh.publish('network_state', state)

    def __set_net(self, event, msg):
        if self.__net_sign == "4G":
            self.__net_sign = "5G"
        else:
            if not msg:
                self.__net_sign = "4G"
        EventMesh.publish("publish_net_show")

    def __net_cb(self, event, msg):
        EventMesh.publish("net_show", self.__net_sign)

    def post_processor_after_initialization(self, *args, **kwargs):
        """
        ??????????????????
        :param args:
        :param kwargs:
        :return:
        """
        if sim.getStatus() != -1:
            stagecode, subcode = self.wait_connect(30)
            if stagecode == 1 and subcode != 1:
                state = 1
            elif stagecode == 3 and subcode == 1:
                state = 2
            elif stagecode == 2:
                state = 3
            else:
                state = 3
            self.start_keepalive()
        else:
            print("??????????????? ~~~~")
            state = 1
        EventMesh.publish('network_state', state)

    def start_keepalive(self):
        self.timer.start(self.check_net_timeout, 1, self.__check)

    def set_keepalive(self, event, msg):
        self.timer.stop()
        self.check_net_timeout = msg
        self.start_keepalive()

    def __check(self, args):
        net_state = self.get_net_status()
        if net_state == 2:
            if self.error_count:
                EventMesh.publish('network_state', net_state)
                self.error_count = 0
        else:
            self.error_count += 1
            EventMesh.publish('network_state', net_state)

    def wait_connect(self, timeout):
        self.check_net.poweron_print_once()
        return self.check_net.wait_network_connected(timeout)

    def get_net_status(self):
        if self.__data_call.getInfo(1, 0) != -1:
            result = 2 if self.__data_call.getInfo(1, 0)[2][0] else 3
            return result
        else:
            return 3


class PocManager(Abstract):
    BAND_CALL = 1
    BND_LISTEN_START = 4
    BND_LISTEN_STOP = 6
    BND_SPEAK_STOP = 3
    PTT_ON = 1
    PTT_OFF = 0

    def __init__(self):
        self.state = 1
        self.session_info = None
        self.log = LogAdapter(self.__class__.__name__)
        self.__call_time_status = False
        self.__call_member_timer = osTimer()
        self.__low_power_mode_timer = osTimer()
        self.__lcd_sleep_timer = osTimer()
        self.__low_power_mode = 30
        self.__single_call_quit_time = 30
        self.__lcd_sleep_time = 30
        self.__gps_img_show = 0
        self.__login_state = False
        self.__platform = None
        self.__sim_mode = None
        self._user = None
        self.group_name = None
        self.tts_play_enable = True
        self.speak_close_first = False
        self.error_msg = ""
        self.__rocker_arm = 0
        self.cloud_check_timer = osTimer()
        self.__cell_timer = osTimer()
        self.__weather_timer = osTimer()
        self.__handler_error_ptt_timer = osTimer()
        self.__keypad_tone = 1
        self.__ptt_hint_tone = 1
        self.weather_msg_list = list()
        self.last_join_group = None
        self.main_call_end_state = False
        self.platform_dict = {
            0: "xin",
            1: "std"
        }

    def ping(self, *args):
        poc.send_ping()

    def post_processor_after_instantiation(self, *args, **kwargs):
        EventMesh.subscribe("screen_speak", self.group_call)
        EventMesh.subscribe("screen_speak_end", self.call_end)
        EventMesh.subscribe("main_get_group_cur", self.get_group_name)
        EventMesh.subscribe("about_get_user", self.about_user)
        EventMesh.subscribe("group_get_list", self.get_group_list)
        EventMesh.subscribe("group_enterbtn_click", self.join_group)
        EventMesh.subscribe("member_speakbtn_click", self.call_member)
        EventMesh.subscribe("check_call_member_status", self.check_call_member_status)
        EventMesh.subscribe("exit_call_member", self.exit_call_member)
        EventMesh.subscribe("member_get_list", self.get_member_list)
        EventMesh.subscribe("group_count", self.get_group_count)
        EventMesh.subscribe("member_count", self.get_member_count)
        EventMesh.subscribe("media-tts-play", self.tts_play)
        EventMesh.subscribe("set_poc_low_power_mode", self.set_lower_power)
        EventMesh.subscribe("get_poc_low_power_mode", self.get_lower_power)
        EventMesh.subscribe("set_lcd_sleep_mode", self.set_lcd_sleep_mode)
        EventMesh.subscribe("get_lcd_sleep_mode", self.get_lcd_sleep_mode)
        EventMesh.subscribe("get_single_call_quit_time", self.get_single_call_quit_time)
        EventMesh.subscribe("set_single_call_quit_time", self.set_single_call_quit_time)
        EventMesh.subscribe("request_lbs_info", self.request_lbs_info)
        EventMesh.subscribe("request_weather_info", self.get_weather_info)
        EventMesh.subscribe("std_write_iccid", self.std_write_iccid)
        EventMesh.subscribe("get_poc_platform", self.get_poc_platform)
        EventMesh.subscribe("set_poc_platform", self.set_poc_platform)
        EventMesh.subscribe("set_poc_ptt_hint_tone", self.set_poc_ptt_hint_tone)
        EventMesh.subscribe("get_poc_ptt_hint_tone", self.get_poc_ptt_hint_tone)
        EventMesh.subscribe("set_poc_keypad_tone", self.set_poc_keypad_tone)
        EventMesh.subscribe("get_poc_keypad_tone", self.get_poc_keypad_tone)
        EventMesh.subscribe("get_sim_mode", self.get_sim_mode)
        EventMesh.subscribe("set_sim_mode", self.set_sim_mode)
        EventMesh.subscribe("get_login_state", self.get_login_state)
        EventMesh.subscribe("get_speaker_state", self.get_speaker_state)
        EventMesh.subscribe("get_gps_img_state", self.get_gps_img_state)
        EventMesh.subscribe("about_get_rocker_arm", self.about_get_rocker_arm)
        EventMesh.subscribe("get_poc_cloud_state", self.get_poc_cloud_state)
        EventMesh.subscribe("reset_login_status_cb", self.reset_login_status_cb)
        EventMesh.subscribe("close_speaker", self.close_speaker)
        self.sync_setting_config()

    def about_get_rocker_arm(self, topic, msg):
        return self.__rocker_arm

    def sync_setting_config(self):
        self.__low_power_mode = EventMesh.publish("persistent_config_get", "low_power_mode")
        self.__single_call_quit_time = EventMesh.publish("persistent_config_get", "quit_call_time")
        self.__lcd_sleep_time = EventMesh.publish("persistent_config_get", "lcd_sleep_time_mode")
        self.__platform = EventMesh.publish("persistent_config_get", "platform")
        self.__sim_mode = EventMesh.publish("persistent_config_get", "sim_mode")
        self.__ptt_hint_tone = EventMesh.publish("persistent_config_get", "ptt_hint_tone")
        self.__keypad_tone = EventMesh.publish("persistent_config_get", "keypad_tone")
        self.lower_power_start()
        self.ptt_tone_switch()

    def ptt_tone_switch(self):
        # __ptt_hint_tone?????????Tone????????????, ????????????1-?????????
        poc.Set_Tone_Switch(1 - self.__ptt_hint_tone)

    def set_lcd_sleep_mode(self, event, mode):
        if self.__lcd_sleep_time == mode:
            return
        print("set_lcd_sleep_mode mode = {}".format(mode))
        self.__lcd_sleep_time = mode
        EventMesh.publish("persistent_config_store", {"lcd_sleep_time_mode": self.__lcd_sleep_time})

    def get_lcd_sleep_mode(self, event, mode):
        return self.__lcd_sleep_time

    def get_poc_platform(self, event, mode):
        return self.__platform

    def get_single_call_quit_time(self, event=None, mode=None):
        return self.__single_call_quit_time

    def set_single_call_quit_time(self, event=None, mode=None):
        self.__single_call_quit_time = mode
        EventMesh.publish("persistent_config_store", {"quit_call_time": self.__single_call_quit_time})

    def lower_power_start(self, event=None, mode=None):
        """???????????????"""
        self.__low_power_mode_timer.start(self.__low_power_mode * 1000, 1, self.ping)

    def set_lower_power(self, event=None, mode=None):
        """?????????????????????"""
        self.__low_power_mode_timer.stop()
        self.__low_power_mode = mode
        self.lower_power_start()
        EventMesh.publish("persistent_config_store", {"low_power_mode": mode})

    def set_poc_platform(self, event=None, mode=None):
        if EventMesh.publish("persistent_config_get", "platform") != mode:
            EventMesh.publish("persistent_config_store", {"platform": mode})
            utime.sleep(2)
            Power.powerRestart()

    def set_poc_ptt_hint_tone(self, event=None, mode=None):
        EventMesh.publish("persistent_config_store", {"ptt_hint_tone": mode})
        self.__ptt_hint_tone = mode
        self.ptt_tone_switch()

    def get_poc_ptt_hint_tone(self, event=None, mode=None):
        return self.__ptt_hint_tone

    def set_poc_keypad_tone(self, event=None, mode=None):
        EventMesh.publish("persistent_config_store", {"keypad_tone": mode})
        self.__keypad_tone = mode

    def get_poc_keypad_tone(self, event=None, mode=None):
        return self.__keypad_tone

    def get_lower_power(self, event=None, mode=None):
        return self.__low_power_mode

    def get_sim_mode(self, event=None, mode=None):
        return self.__sim_mode

    def set_sim_mode(self, event=None, mode=None):
        EventMesh.publish("persistent_config_store", {"sim_mode": mode})
        self.__sim_mode = mode
        return self.get_sim_mode()

    def post_processor_after_initialization(self, *args, **kwargs):
        print("poc init with sim status = {}".format(sim.getStatus()))
        while 1:
            init_status = poc.get_init_status()
            if init_status != 0:
                break
            utime.sleep(1)
        poc.init(self.__init_cb)
        poc.set_tts_enable(1)
        poc.set_notify_mode(1)
        poc.set_solution("HF")
        poc.set_solution_version("0924")
        poc.set_productInfo("HF")
        poc.set_manufacturer("HF")
        poc.write_custom(poc.Change_Platform_Context, self.platform_dict.get(self.__platform))
        # ??????
        poc.login(self.__login_status_cb)
        # ??????????????????
        poc.register_join_group_cb(self.__join_group_cb)
        # # ??????????????????
        poc.register_audio_cb(self.__audio_cb)
        # ????????????????????????
        poc.register_listupdate_cb(self.__listupdate_cb)
        # ????????????????????????
        poc.register_request_lbs_info_cb(self.request_lbs_info_cb)
        # ????????????????????????
        poc.register_weather_info_cb(self.request_weather_info_cb)
        # ??????????????????
        poc.register_error_cb(self.error_handler)
        # ????????????????????????
        poc.register_location_change_cb(self.location_change_cb)
        poc.register_cell_location_change_cb(self.cell_location_cb)
        # ??????????????????
        poc.register_member_audio_enable_cb(self.member_audio_enable_cb)

    def member_audio_enable_cb(self, *args):
        print("member_audio_enable_cb {}".format(args))
        self.__rocker_arm = args[0]

    def get_gps_img_state(self, event=None, msg=None):
        EventMesh.publish("gps_img_state", self.__gps_img_show)

    def cell_location_cb(self, msg):
        print("cell_location_cb -----------------  {}".format(msg))
        if not self.__gps_img_show:
            if msg[0]:
                self.__gps_img_show = msg[0]
                self.__cell_timer.start(msg[1] * 1000, 1, self.upload_cell)
        self.get_gps_img_state()

    def upload_cell(self, *args):
        poc.send_gpsinfo(0.0, 0.0, utime.localtime(), 0.0, 0.0, 0.0)

    def location_change_cb(self, msg):
        if not self.__gps_img_show:
            if msg[0]:
                self.__gps_img_show = msg[0]
                self.__cell_timer.start(msg[1] * 1000, 1, self.upload_cell)
        self.get_gps_img_state()
        print("location_change_cb {}".format(msg))

    def error_handler(self, *args):
        print("error args = {}".format(args))
        self.error_msg = args[0]

    def get_poc_cloud_state(self, event, msg):
        return poc.get_loginstate()

    def reset_login_status_cb(self, event, msg):
        self.__login_status_cb(msg)

    def __init_cb(self, msg):
        self.log.info("poc init (state) -> {}".format(msg))

    def check_cloud_connect(self, *args):
        state = EventMesh.publish("get_poc_cloud_state")
        print("cloud connect state {}".format(state))
        if state == 1:
            self.cloud_check_timer.stop()
            EventMesh.publish("reset_login_status_cb", 1)
            EventMesh.publish("reset_led_timer", 2)

    def __login_status_cb(self, para):
        self.log.debug("ui_login_status {}".format(para))
        # ????????????????????????????????????????????????????????????
        EventMesh.publish("check_cloud_state", para)
        self.cloud_check_timer.stop()
        if para == 1:
            self.publish_state("?????????")
        else:
            self.cloud_check_timer.start(5000, 1, self.check_cloud_connect)
            self.publish_state("?????????")

    def __audio_cb(self, params):
        global PA_Play_State
        self.log.debug("audio state:  {} uid : {} name {} flag {}".format(*params))
        if params[0] == self.BAND_CALL:
            EventMesh.publish("set_PA_Play_State", 1)
            self.main_call_end_state = False
            self.state = 3
        elif params[0] == self.BND_LISTEN_START:
            print("params = {}".format(params))
            if params[-1] == 0:
                # ???????????????
                self.state = 0
            else:
                self.state = 2
            EventMesh.publish("lcd_state_manage")  # ??????LCD
            EventMesh.publish("lcd_sleep_timer_stop")  # ??????LCD????????????
            EventMesh.publish("ptt_receive_led", 1)
            EventMesh.publish("check_call_member_status", 1)
            self.session_info = params[2]
            state_msg = "{}????????????".format(self.session_info)
            EventMesh.publish("update_session_info", state_msg)
            EventMesh.publish("add_user_btn_style", 0)
            EventMesh.publish("group_cur", state_msg)
            self.log.debug("state - {}".format(self.state))
        elif params[0] == self.BND_LISTEN_STOP or params[0] == self.BND_SPEAK_STOP:
            self.error_msg = ""
            self.state = 1
            self.__handler_error_ptt_timer.stop()
            self.__handler_error_ptt_timer.start(200, 0, self.__error_ptt_handler)
            utime.sleep_ms(100)
        else:
            pass

    def __error_ptt_handler(self, *args):
        print("error_msg = {}".format(self.error_msg))
        if not self.error_msg:
            dev_usr = EventMesh.publish("about_get_user")
            EventMesh.publish("lcd_state_manage")  # ??????LCD????????????
            group_msg = EventMesh.publish("main_get_group_cur")
            EventMesh.publish("ptt_receive_led", 0)
            EventMesh.publish("ptt_led", 0)
            if self.session_info:
                session_info = self.session_info
            else:
                if not self.__rocker_arm:
                    session_info = "?????????????????????"
                else:
                    session_info = "??????"
            print("self.main_call_end_state={} update_session_info {}({})".format(self.main_call_end_state,
                                                                                  dev_usr, session_info))
            # ????????????call????????????
            if not self.main_call_end_state:
                EventMesh.publish("update_session_info", "{}({})".format(dev_usr, session_info))
                EventMesh.publish("clear_user_btn_style")
            else:
                self.main_call_end_state = False
            EventMesh.publish("group_cur", group_msg)
            EventMesh.publish("check_call_member_status", 0)
        else:
            self.state = 1
            if self.error_msg == "???????????????" or self.error_msg == "???????????????????????????":
                EventMesh.publish("set_PA_Play_State", 0)
                self.error_msg = ""
                EventMesh.publish("audio_tone")
                EventMesh.publish("lcd_state_manage")  # ??????LCD????????????

    def __listupdate_cb(self, param):
        if param == 1:
            EventMesh.publish("update_group_info")
        else:
            EventMesh.publish("update_member_info")

    def __join_group_cb(self, para):
        """
        ????????????
        """
        if not para[-1]:
            return
        self.log.info("join group callback (para) -> {}".format(para))
        group_cur = poc.group_getbyid(0)
        EventMesh.publish("lcd_state_manage")  # ??????LCD
        if isinstance(group_cur, list):
            self.log.info(
                "speak ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ success {} -------------------------".format(group_cur))
            now_group_name = group_cur[1]
            if not group_cur[2]:
                self.last_join_group = group_cur
                self.__call_time_status = False
                self.__call_member_timer.stop()
            if not self.group_name:
                self.group_name = now_group_name
            else:
                if self.group_name == now_group_name:
                    self.tts_play_enable = False
                else:
                    self.tts_play_enable = True
                self.group_name = now_group_name
            if self.__login_state:
                tts_msg = "????????????" + self.group_name
            else:
                tts_msg = self.about_user() + "?????????" + "????????????" + self.group_name
                self.tts_play_enable = True
            EventMesh.publish("group_cur", self.group_name)
            EventMesh.publish("main_group_cur", self.group_name)
            if not self.__login_state:
                self.__login_state = True
            if self.tts_play_enable:
                EventMesh.publish("media-tts-play", (tts_msg, 1))
                if not self.__rocker_arm:
                    EventMesh.publish("group_cur", "?????????????????????")
                    EventMesh.publish("update_session_info", "?????????????????????")
                    if not self.speak_close_first:
                        self.speak_close_first = True
                        EventMesh.publish_async("close_speaker")
            if group_cur[2]:
                self.__call_time_status = True
                self.__call_member_timer.start(self.__single_call_quit_time * 1000, 0, self.exit_call_member)

    def close_speaker(self, event, msg):
        utime.sleep(7)
        EventMesh.publish("media-tts-play", ("?????????????????????", 1))

    def get_login_state(self, event, msg):
        return self.__login_state

    def get_member(self):
        return poc.member_getbyid(0)

    def tts_play(self, event, msg):
        poc.play_tts(*msg)

    def __calluser_callback(self, msg):
        """??????????????????"""
        self.log.info("call user callback (msg) -> {}".format(msg))

    def poc_speak(self, value):
        """
        ??????
        :param value:1 ?????? ???0 ????????????
        """
        poc.speak(value)

    def get_member_list(self, event=None, msg=None):
        """??????????????????"""
        group_cur = poc.group_getbyid(0)
        member_count = poc.get_membercount(group_cur[0])
        member_list = poc.get_memberlist(group_cur[0], 0, member_count)
        return member_count, member_list

    @staticmethod
    def publish_state(msg=None):
        """????????????"""
        return EventMesh.publish("state", msg)

    def get_speaker_state(self, event, msg):
        return self.state

    def group_call(self, event, msg=None):
        """
        ????????????
        :param event:
        :param msg:
        """
        if self.state:
            self.poc_speak(1)
            if self.group_name == "?????????":
                EventMesh.publish("update_session_info", "?????????")
                EventMesh.publish("audio_tone")
            else:
                if not self.__rocker_arm:
                    EventMesh.publish("group_cur", "?????????????????????")
                    EventMesh.publish("update_session_info", "?????????????????????")
                else:
                    EventMesh.publish("update_session_info", "??????????????????")
                    EventMesh.publish("group_cur", "??????????????????")
            EventMesh.publish("add_user_btn_style", 1)
            EventMesh.publish("lcd_state_manage")  # ??????LCD
        else:
            EventMesh.publish("audio_tone")
        return 1
        # return 0

    def call_end(self, event, msg):
        """
        ????????????
        :param event:
        :param msg:
        """
        if self.state:
            self.poc_speak(0)
            utime.sleep_ms(100)
            group_msg = EventMesh.publish("main_get_group_cur")
            EventMesh.publish("group_cur", group_msg)
            dev_usr = EventMesh.publish("about_get_user")
            if not self.__rocker_arm:
                EventMesh.publish("update_session_info", "{}(?????????????????????)".format(dev_usr))
            else:
                EventMesh.publish("update_session_info", "{}(??????)".format(dev_usr))
                self.main_call_end_state = True
                print("update_session_info", "{}(??????)".format(dev_usr))
            EventMesh.publish("clear_user_btn_style")

    def get_group_list(self, event=None, msg=None):
        """
        ????????????????????????
        :param event:
        :param msg:
        :return:
        """
        group_count = poc.get_groupcount()
        group_list = poc.get_grouplist(0, group_count)
        return group_count, group_list

    def get_group_name(self, event=None, msg=None):
        """
        ??????????????????
        :param event:
        :param msg:
        :return
        """
        if not self.group_name:
            group_cur = poc.group_getbyid(0)
            if isinstance(group_cur, list):
                self.group_name = group_cur[1]
        if not self.group_name:
            self.group_name = "?????????"
        return self.group_name

    def join_group(self, event=None, msg=None):
        """
        ??????????????????
        :param event:
        :param msg:
        :return:
        """
        poc.leavegroup()
        (count, group_list) = self.get_group_list()
        self.log.info("count = {} group_list = {} msg = {}".format(count, group_list, msg))
        poc.joingroup(group_list[msg][0])

    def call_member(self, event=None, msg=None):
        """
        ??????????????????
        :param event:
        :param msg:
        :return
        """
        call_sta = poc.callusers(msg, self.__calluser_callback)
        return call_sta

    def exit_call_member(self, *args):
        '''
        ????????????
        '''
        if self.__call_time_status:
            group_cur = poc.group_getbyid(0)
            print("exit call member {} group_cur {}".format(self.__call_time_status, group_cur))
            self.__call_time_status = False
            member_count = self.get_member_count()
            print("leavegroup {} member_count = {} last_join_group = {}".format(self.about_user(), member_count,
                                                                                self.last_join_group))
            state = poc.leavegroup()
            if group_cur[1] != self.about_user():
                group_cur = poc.group_getbyid(0)
                print("join new group member {} group_cur {}".format(self.__call_time_status, group_cur))
                if member_count > 1:
                    if self.last_join_group:
                        poc.joingroup(self.last_join_group[0])
        else:
            return -1

    def check_call_member_status(self, topic, mode):
        '''
        ?????????????????????????????????
        mode: 1-PTT?????????0-PTT?????????2-????????????????????????
        '''
        if not self.__call_time_status:
            return
        if mode == PocManager.PTT_ON:
            self.__call_member_timer.stop()
        elif mode == PocManager.PTT_OFF:
            self.__call_member_timer.start(self.__single_call_quit_time * 1000, 0, self.exit_call_member)
        else:
            self.__call_time_status = False
            poc.leavegroup()
            self.__call_member_timer.stop()

    def get_member_count(self, event=None, msg=None):
        """
        ????????????????????????
        :param event:
        :param msg:
        :return:
        """
        group_cur = poc.group_getbyid(0)
        member_count = poc.get_membercount(group_cur[0])
        return member_count

    def get_group_count(self, event=None, msg=None):
        """
        ????????????????????????
        :param event:
        :param msg:
        :return:
        """
        return poc.get_groupcount()

    def about_user(self, event=None, msg=None):
        """
        ??????????????????
        :param event:
        :param msg:
        :return:
        """
        if not self._user:
            self._user = self.get_member()[1]
        return self._user

    def request_lbs_info_cb(self, data):
        print("lbs info = {}".format(data))
        EventMesh.publish("lbs_result_event", data)

    def request_lbs_info(self, event=None, msg=None):
        poc.request_lbs_info(128, 128, 0.0, 0.0)

    def request_weather_info_cb(self, data):
        print("weather info = {}".format(data))
        if data and data[0] != "":
            if not self.weather_msg_list:
                self.weather_timer_task()
            self.weather_msg_list = []
            weather_msg = data[0].split(",")
            index_num = 0
            end_num = 4
            for i in range(0, 3):
                msg = weather_msg[index_num:end_num]
                index_num += 4
                end_num += 4
                climate = msg[0]
                if "???" in climate:
                    weather_state = ("???", "B:/static/qing.png")
                elif "???" in climate:
                    weather_state = ("??????", "B:/static/duoyun.png")
                elif "???" in climate:
                    weather_state = ("???", "B:/static/yu.png")
                elif "???" in climate:
                    weather_state = ("???", "B:/static/feng.png")
                elif "???" in climate:
                    weather_state = ("???", "B:/static/wu.png")
                elif "???" in climate:
                    weather_state = ("???", "B:/static/xue.png")
                else:
                    weather_state = ("??????", "B:/static/duoyun.png")
                temperature = "%s???~%s???" % (msg[3].split("???")[1], msg[1].split("???")[1])
                self.weather_msg_list.append((weather_state, temperature))
            self.weather_msg_list.append(data)
        else:
            pass
        EventMesh.publish("weather_result_event", self.weather_msg_list)
        EventMesh.publish("update_weather", self.weather_msg_list)

    def get_weather_info(self, event=None, msg=None):
        if self.weather_msg_list:
            EventMesh.publish("weather_result_event", self.weather_msg_list)
            EventMesh.publish("update_weather", self.weather_msg_list)
        else:
            self.request_weather_info()

    def request_weather_info(self, msg=None):
        state = poc.request_weather_info(0.0, 0.0)
        if not state:
            poc.request_weather_info(0.0, 0.0)

    def weather_timer_task(self):
        now_time = utime.localtime()
        now_timestamp = utime.mktime(now_time)
        if now_time[3] != 0:
            list_now_time = list(now_time)
            list_now_time[3] = 23
            list_now_time[4] = 59
            next_timestamp = utime.mktime(tuple(list_now_time)) + 360
            next_timer_t = next_timestamp - now_timestamp
        else:
            next_timer_t = 86400
        self.__weather_timer.start(next_timer_t * 1000, 0, self.request_weather_info)

    def std_write_iccid(self, event=None, iccid=None):
        poc.write_custom(poc.Account_Login_Enable, "1")
        poc.write_custom(poc.Write_Custom_Account, iccid)
