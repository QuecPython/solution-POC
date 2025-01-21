import utime
import _thread
import osTimer
import ql_fs
import queue
import sim
import net
import modem
import pm
import poc
import audio
import dataCall
import checkNet
import SecureData
from misc import ADC, USB, Power
from machine import Pin, ExtInt

try:
    from common import AbstractLoad, EventMap, PrintLog
except:
    from usr.common import AbstractLoad, EventMap, PrintLog



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

# ADC0 引脚19
class Battery(object):
    """This class is for battery info.

    This class can get battery voltage and energy.
    if adc_args is not None, use adc to read battery

    adc_args: (adc_num, adc_period, factor)

        adc_num: ADC channel num
        adc_period: Cyclic read ADC cycle period
        factor: calculation coefficient
    """

    def __init__(self, adc_args=None, chrg_gpion=None, stdby_gpion=None):
        self.__energy = 100
        self.__temp = 20

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
            volts = sorted(BATTERY_OCV_TABLE["nix_coy_mnzo2"][key].keys(), reverse=True)  # 进行降序排列
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
            if temp > 30:  # 不同的温度范围
                return self.__get_soc_from_dict(55, volt_arg)
            elif temp < 10:
                return self.__get_soc_from_dict(0, volt_arg)
            else:
                return self.__get_soc_from_dict(20, volt_arg)

    def __get_power_vbatt(self):
        test_vbatt = sum([Power.getVbatt() for i in range(100)])
        # print("__get_power_vbatt test vbatt : {}".format(test_vbatt))
        return int(test_vbatt / 100)

    def __get_adc_vbatt(self):
        self.__adc.open()  # adc获取电压值
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
        # self.__energy = self.__get_soc(self.__temp, self.get_voltage())
        self.__energy = self.get_voltage()
        return self.__energy

    def set_charge_callback(self, charge_callback):
        if self.__chrg_gpion is not None and self.__stdby_gpion is not None:
            if callable(charge_callback):
                self.__charge_callback = charge_callback
                return True
        return False

    def get_charge_status(self):
        return self.__charge_status


class BatteryManager(AbstractLoad):
    def __init__(self):
        """电池管理器"""
        self.battery = Battery()
        self.low_battery = False

    def instance_after(self):
        """订阅此类所有的事件到 EventMesh中"""
        EventMap.bind("get_battery", self.get_battery)

    def get_battery(self, event=None, msg=None):
        battery = self.battery.get_energy()
        return battery





class DevInfoService(AbstractLoad):
    def __init__(self):
        self.usb = USB()
        self.week_list = ["一","二","三","四","五","六","日"]

    def instance_after(self):
        EventMap.bind("devinfoservice__get_time", self.__get_time)
        EventMap.bind("screen_get_battery", self.__get_battery)
        EventMap.bind("screen_get_signal", self.__get_signal)
        EventMap.bind("devinfoservice__get_firmware", self.__get_firmware)
        EventMap.bind("devinfoservice__get_usb_status", self.__get_usb_status)
        EventMap.bind("devinfoservice__get_iccid", self.__get_iccid)
        EventMap.bind("devinfoservice__get_imei", self.__get_imei)
        EventMap.bind("devinfoservice__get_device_operator", self.__get_device_operator)

    def __get_time(self, event=None, msg=None):
        local_time = utime.localtime()
        date = "{:04}-{:02}-{:02}".format(local_time[0], local_time[1], local_time[2])
        time = "{:02}:{:02}:{:02}".format(local_time[3], local_time[4], local_time[5])
        result = [date, time, self.week_list[local_time[6]]]
        return result

    def __get_firmware(self, *args):
        '''
        获取设备固件版本号
        '''
        fw_version = modem.getDevFwVersion().replace('_OCPU_', '_')
        fw_version = fw_version.replace('TEST', 'BETA')
        if isinstance(fw_version, str):
            return fw_version
        return "--"

    def __get_usb_status(self, event=None, msg=None):
        state = self.usb.getStatus()
        if state == -1: state = 0
        return state
    
    def __get_iccid(self, event, msg):
        iccid = sim.getIccid()
        if -1 == iccid:
            iccid = None
        else:
            dev_ope = self.__get_device_operator()
            if'中国电信' == dev_ope or '中国联通' == dev_ope:
                iccid = iccid[0:19]
        return iccid
    
    def __get_imei(self, event, msg):
        imei = modem.getDevImei()       
        if -1 == imei: imei = None
        return imei

    def __get_device_operator(self, event=None, msg=None):
        """
        获取设备运营商
        """
        net_ope_map = {
            "46001": "中国联通", "46006": "中国联通", "46009": "中国联通", "46010": "中国联通",
            "46000": "中国移动", "46002": "中国移动", "46004": "中国移动", 
            "46007": "中国移动", "46020": "中国移动", "46008": "中国移动", "46013": "中国移动",
            "46003": "中国电信", "46005": "中国电信", "46011": "中国电信", "46012": "中国电信"
        }
        """获取运营商"""
        try:
            _imsi = sim.getImsi()[0:5]  # 获取当前网络的运营商信息简称
        except Exception:
            return "无"
        return net_ope_map.get(_imsi, None)
    
    def get_device_fw_version(self, *args):
        '''
        获取设备固件版本号
        '''
        fw_version = modem.getDevFwVersion()
        if isinstance(fw_version, str):
            return fw_version
        return "--"  

    def __get_battery(self, event=None, msg=None):
        """
        获取电池事件,暂时没支持
        :param event:
        :param msg:
        :return:
        """
        value = EventMap.send("get_battery")
        if value < 3380:
            level = 0
        elif value < 3630:
            level = 1
        elif value < 3830:
            level = 2
        elif value < 4023:
            level = 3
        else:
            level = 4
        if self.get_usb_state():
            img_path = 'U:/img/charge_battery.png'
        else:
            img_path = 'U:/img/battery_' + str(level) + '.png'
        return img_path
    
    def __get_signal(self, event=None, msg=None):
        return net.csqQueryPoll()
    
    def get_usb_state(self, event=None, msg=None):
        state = self.usb.getStatus()
        if state == -1:
            state = 0
        return state




class MediaService(AbstractLoad):
    """
    媒体服务
    """
    def __init__(self):
        self.aud = audio.Audio(0)  # 0听筒 1耳机 2喇叭
        self.tts = audio.TTS(0)
        self.tts.setVolume(9)
        self.q = queue.Queue()
        
        self.mic_det = ExtInt(ExtInt.GPIO14, ExtInt.IRQ_RISING_FALLING, ExtInt.PULL_PU, self.__mic)
        self.mic_det.enable()
        self.p1 = Pin(Pin.GPIO1, Pin.OUT, Pin.PULL_DISABLE, 0)
        self.aud.set_pa(Pin.GPIO1, 4)
        self.mute_value = 0
        self.mute = 0
        
        self.noise_reduction_switch = Pin(Pin.GPIO38, Pin.OUT, Pin.PULL_DISABLE, 0)

    def __mic(self, args):
        if args[1]:
            EventMap.send("update_ej_img", 0)
        else:
            EventMap.send("update_ej_img", 1)

    def instance_after(self):
        EventMap.bind("mediaservice__noise_reduction_enable", self.__noise_reduction_enable)
        EventMap.bind("mediaservice__get_mic_det_state", self.__get_mic_det_state)
        EventMap.bind("mediaservice__audio_tone", self.__audio_tone)
        EventMap.bind("mediaservice__beep_tone", self.__beep_tone)
        EventMap.bind("mediaservice__tts_play", self.__tts_play)
        EventMap.bind("mediaservice__tts_stop", self.__tts_stop)
        poc.set_vol(1, 8)
        poc.set_vol(2, 1)

    def __noise_reduction_enable(self, event, msg):
        if msg:
            self.noise_reduction_switch.write(1)
        else:
            self.noise_reduction_switch.write(0)  

    def __beep_tone(self, event, msg):
        if self.q.empty():
            self.q.put(None)

    def __audio_tone(self, event, msg):
        self.aud.aud_tone_play(16, 100)

    def __get_mic_det_state(self, event=None, msg=None):
        return self.mic_det.read_level() 

    def __tts_play(self, event=None, msg=None):
        if msg[0][0] == '0':
            self.tts.play(4, msg[1], 2, '[n1]' + msg[0])
        else:
            poc.play_tts(msg[0], msg[1])

    def __tts_stop(self, event, msg):
        self.tts.stop()     



class NetService(AbstractLoad):
    """
    网络服务
    """
    THRESHOLD = 10

    def __init__(self):
        self.__check_net = checkNet.CheckNetwork("QuecPython_EC600M_CN", "Poc_Demo_v1.0")
        self.__check_net_timer = osTimer()
        self.__check_net_timeout = 60 * 1000
        self.__check_net_error_count = 0
        self.__net_generation = "4G"

    def instance_after(self, *args, **kwargs): 
        EventMap.bind("netservice__set_net_keepalive", self.__set_net_keepalive)
        EventMap.bind("netservice__set_net_generation", self.__set_net_generation)
        EventMap.bind("netservice__get_net_generation", self.__get_net_generation)
        
        # 当网络状态发生变化，比如断线、上线时，调用回调
        dataCall.setCallback(self.__datacall_callback)

    def load(self, *args, **kwargs):
        status = 1
        if sim.getStatus():
            self.__check_net.poweron_print_once()
            stagecode, subcode = checkNet.waitNetworkReady(30)
            if stagecode == 1 and subcode != 1:
                status = 1
            elif stagecode == 3 and subcode == 1:
                status = 2
            elif stagecode == 2:
                status = 3
            else:
                status = 3
            self.__do_net_check()
            self.__set_net_keepalive(event=None, msg=self.__check_net_timeout)  # 手动开启心跳检测
        EventMap.send('welcomescreen__net_status', status)

    def __datacall_callback(self, args):
        # pdp = args[0]
        nw_sta = args[1]
        if nw_sta == 1: # 1 网络已连接
            EventMap.send("mediaservice__tts_play", ("网络已连接", 0))
            EventMap.send('welcomescreen__net_status', 2)
            PrintLog.log("NetService", "Network connected.")
            self.__net_generation = "4G"
            EventMap.send("menubar__update_net_status", self.__net_generation)
        else:   # 0 网络已断开
            EventMap.send("mediaservice__tts_play", ("网络已断开", 0))
            PrintLog.log("NetService", "Network disconnected.")
            EventMap.send('welcomescreen__net_status', 3)
            self.__net_generation = None
            EventMap.send("menubar__update_net_status", self.__net_generation)

    def __set_net_generation(self, event, msg):
        self.__net_generation = msg

    def __get_net_generation(self, event, msg):
        return self.__net_generation

    def __set_net_keepalive(self, event, msg):
        self.__check_net_timer.stop()
        self.__check_net_timeout = msg
        self.__check_net_timer.start(self.__check_net_timeout, 1, lambda arg: self.__do_net_check()) # 心跳检测

    def __do_net_check(self):
        status = 3
        if dataCall.getInfo(1, 0) != -1:
            status = 2 if dataCall.getInfo(1, 0)[2][0] else 3
        EventMap.send('welcomescreen__net_status', status)


class PocService(AbstractLoad):
    """
    Poc服务
    """
    BAND_CALL = 1
    BND_LISTEN_START = 4
    BND_LISTEN_STOP = 6
    BND_SPEAK_STOP = 3
    PTT_ON = 1
    PTT_OFF = 0

    class CALL_STATE(object):
        IN_CALL = 1     # 主动呼叫
        ON_CALL = 2     # 被呼叫
        CALL_END = 0    # 呼叫结束
        ROB_CALL = 3    # 由于优先级被抢呼

    def __init__(self):
        self.__speaker_status = 1
        self.__call_time_status = False
        self.__call_member_timer = osTimer()
        self.__call_quit_time = 30

        self.__cloud_check_timer = osTimer()
        self.__weather_timer = osTimer()
        self.__last_join_group = None
        self.net_error = False
        self.error_msg = ""
        self._user = None
        self.last_audio = None
        self.__session_info = None
        self.tts_play_enable = True
        self.speak_close_first = False
        self.__rocker_arm = 1
        self.main_call_end_state = False
        self.__ptt_hint_tone = 1
        self.__login_status = False

        self.__platform = 0     # 和配置文件同步, 默认芯平台
        self.__platform_xin = None
        self.__platform_dict = { 0: "xin", 1: "std" }

        self.__user_info = None
        self.__group_name = None
        self.__group_name_default = "current no group"

        self.weather_msg_list = list()
        self.__gps_img_show = 0
        self.__cell_timer = osTimer()

    def instance_after(self, *args, **kwargs):
        EventMap.bind("pocservice__speaker_enable", self.__speaker_enable)
        EventMap.bind("pocservice__close_speaker", self.__close_speaker)
        EventMap.bind("pocservice__set_ptt_hint_tone", self.__set_ptt_hint_tone)
        EventMap.bind("pocservice__join_group", self.__join_group)
        EventMap.bind("pocservice__leave_group", self.__leave_group)
        EventMap.bind("member_speakbtn_click", self.__call_member)
        EventMap.bind("pocservice__call_member_status", self.__call_member_status)
        EventMap.bind("pocservice__call_member_exit", self.__call_member_exit)
        EventMap.bind("pocservice__get_platform", self.__get_platform)
        EventMap.bind("pocservice__set_platform", self.__set_platform) 
        EventMap.bind("pocservice__get_speaker_status", self.__get_speaker_status)
        EventMap.bind("pocservice__get_rocker_arm", self.__get_rocker_arm)
        EventMap.bind("pocservice__get_login_status", self.__get_login_status)
        EventMap.bind("pocservice__set_account", self.__set_account)
        EventMap.bind("pocservice__set_password", self.__set_password)
        EventMap.bind("pocservice__get_user_type", self.__get_user_type)
        EventMap.bind("pocservice__check_xin_platform", self.__check_xin_platform)
        EventMap.bind("pocservice__get_audio_status", self.__get_audio_status)
        EventMap.bind("request_weather_info", self.request_weather_info)
        EventMap.bind("get_gps_img_state", self.get_gps_img_state)
        EventMap.bind("request_lbs_info", self.request_lbs_info)

        EventMap.bind("get_group_name", self.__get_group_name)
        EventMap.bind("about_get_user", self.__about_user)
        EventMap.bind("group_get_list", self.__get_group_list)
        EventMap.bind("member_get_list", self.__get_member_list)
        EventMap.bind("group_count", self.__get_group_count)
        EventMap.bind("member_count", self.__get_member_count)

    def load(self, *args, **kwargs):
        PrintLog.log("PocService", "poc init with sim status = {}".format(sim.getStatus()))
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
        poc.write_custom(poc.Change_Platform_Context, self.__platform_dict.get(self.__platform))
        poc.write_custom(poc.Set_Sync_Record_Stop_Duration, '50')
        poc.write_custom(poc.Set_Tone_Duration, '30')

        # 登录
        poc.login(self.__poc_login_cb)
        # 注册入组回调
        poc.register_join_group_cb(self.__poc_join_group_cb)
        # 注册音频回调
        poc.register_audio_cb(self.__poc_audio_cb)
        # 注册数据更新回调
        poc.register_listupdate_cb(self.__poc_listupdate_cb)
        # 注册定位信息回调
        poc.register_request_lbs_info_cb(self.__poc_request_lbs_info_cb)
        # 注册天气信息回调
        poc.register_weather_info_cb(self.__poc_weather_info_cb)
        # 注册失败接口
        poc.register_error_cb(self.__poc_error_cb)
        # 注册定位改变接口
        poc.register_location_change_cb(self.__poc_location_change_cb)
        poc.register_cell_location_change_cb(self.__poc_cell_location_change_cb)
        # 注册摇臂回调
        poc.register_member_audio_enable_cb(self.__poc_member_audio_enable_cb)
        self.__ptt_tone_switch()

    def __check_cloud_connect(self):  
        status = poc.get_loginstate()
        PrintLog.log("PocService", "cloud connect status {}".format(status))
        if status == 1:
            self.__cloud_check_timer.stop()
            self.__poc_login_cb(1) 
        elif status == 2:
            EventMap.send("welcomescreen__check_cloud_status", 2)

    def __poc_request_lbs_info_cb(self, data):
        print("lbs info = {}".format(data))
        EventMap.send("lbs_result_event", data)

    def request_lbs_info(self, event=None, msg=None):
        poc.request_lbs_info(128, 128, 0.0, 0.0)

    def __poc_cell_location_change_cb(self, msg):
        print("cell_location_cb -----------------  {}".format(msg))
        if not self.__gps_img_show:
            if msg[0]:
                self.__gps_img_show = msg[0]
                self.__cell_timer.start(msg[1] * 1000, 1, self.upload_cell)
        self.get_gps_img_state()

    def __poc_location_change_cb(self, msg):
        print("location_change_cb -----------------  {}".format(msg))
        if not self.__gps_img_show:
            if msg[0]:
                self.__gps_img_show = msg[0]
                self.__cell_timer.start(msg[1] * 1000, 1, self.upload_cell)
        self.get_gps_img_state()

    def get_gps_img_state(self, event=None, msg=None):
        EventMap.send("menubar__update_gps_status", self.__gps_img_show)   

    def upload_cell(self, *args):
        poc.send_gpsinfo(0.0, 0.0, utime.localtime(), 0.0, 0.0, 0.0) 

    def __poc_login_cb(self, param):
        EventMap.send("welcomescreen__check_cloud_status", param) # 登录成功首页显示已登录，且去查询组群信息
        # 已登录
        if param == 1:
            self.net_error = False
            if self.__platform_dict.get(self.__platform) == 'std':
                self.__securedata_xin_clear()
            else:
                self.__securedata_xin_store()
        # 未登录
        else:
            self.__cloud_check_timer.start(5*1000, 1, lambda arg: self.__check_cloud_connect())  
            self.net_error = True
    
    def __poc_join_group_cb(self, param):
        """
        入组回调, 二次入相同群组, 不需要播报提示,
        """
        PrintLog.log("PocService", "poc join group = {}".format(param))
        if not param[-1]:
            return
        group = poc.group_getbyid(0)
        # EventMap.send("lcd_state_manage")  # 唤醒LCD
        if isinstance(group, list):
            now_group_name = group[1]
            if not group[2]:
                self.__last_join_group = group
                self.__call_time_status = False
                self.__call_member_timer.stop()
            if not self.__group_name:
                self.__group_name = now_group_name
            else:
                if self.__group_name == now_group_name:
                    self.tts_play_enable = False
                else:
                    self.tts_play_enable = True
                self.__group_name = now_group_name
            if self.__login_status:
                if group[2]:
                    tts_msg = "进入" + "临时群组" + self.__group_name
                else:
                    tts_msg = "进入群组" + self.__group_name
            else:
                tts_msg = self.__get_user_info() + "已登录" + "进入群组" + self.__group_name
                self.tts_play_enable = True
            # EventMap.send("group_online", self.__get_group_online_count()) 
            # EventMap.send("main_group_cur", self.__group_name) 
            if not self.__login_status:
                self.__login_status = True
            if self.tts_play_enable:
                EventMap.send("mediaservice__tts_play", (tts_msg, 1))
                if not self.__rocker_arm:
                    # EventMap.send("group", "您已被关闭发言")
                    # EventMap.send("update_session_info", "您已被关闭发言")
                    if not self.speak_close_first:
                        self.speak_close_first = True
                        EventMap.send("pocservice__close_speaker",None ,EventMap.MODE_ASYNC)
            if group[2]:
                self.__call_time_status = True
                self.__call_member_timer.start(self.__call_quit_time * 1000, 0, lambda arg: self.__call_member_exit())

    def __poc_audio_cb(self, params):
        PrintLog.log("PocService", "poc audio: {}".format(params))
        if params[0] == self.BAND_CALL:
            self.main_call_end_state = self.CALL_STATE.IN_CALL
            self.__speaker_status = 3
            self.last_audio = params[0]

        elif params[0] == self.BND_LISTEN_START:
            self.last_audio = params[0]
            self.main_call_end_state = self.CALL_STATE.CALL_END
            if params[-1] == 0:
                self.__speaker_status = 0   # 不允许打断
            else:
                self.__speaker_status = 2
            self.__session_info = params[2]
            state_msg = self.__session_info    
            EventMap.send("load_msgbox", state_msg)
            EventMap.send("poc_play_status", True)
            EventMap.send("menubar__update_poc_status", 2)
            EventMap.send("pocservice__call_member_status", 1)

        elif params[0] == self.BND_LISTEN_STOP or params[0] == self.BND_SPEAK_STOP:
            # 需要判断是否是高等级打断播放
            if params[0] == self.BND_LISTEN_STOP and self.main_call_end_state == self.CALL_STATE.IN_CALL:
                return
            if params[0] == self.BND_LISTEN_STOP:
                self.__speaker_status = params[-1]
            self.__error_ptt_handler(params)
        else:
            pass

    def __poc_listupdate_cb(self, param):
        # if param == 1:
        #     if 0 == poc.get_groupcount():
        #         self.__group_name = self.__group_name_default
        # else:
        #     pass
        if param == 1:
            EventMap.send("update_group_info")
        else:
            EventMap.send("update_member_info")

    def __poc_weather_info_cb(self, data):
        # 天气信息发生变化触发回调
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
                if "晴" in climate:
                    weather_state = ("qing", "U:/img/qing.png")
                elif "云" in climate:
                    weather_state = ("duoyun", "U:/img/duoyun.png")
                elif "雨" in climate:
                    weather_state = ("yu", "U:/img/yu.png")
                elif "风" in climate:
                    weather_state = ("feng", "U:/img/feng.png")
                elif "雾" in climate:
                    weather_state = ("wu", "U:/img/wu.png")
                elif "雪" in climate:
                    weather_state = ("xue", "U:/img/xue.png")
                else:
                    weather_state = ("duoyun", "U:/img/duoyun.png")
                temperature = "%s'C~%s'C" % (msg[3].split("度")[1], msg[1].split("度")[1])
                self.weather_msg_list.append((weather_state, temperature))
            self.weather_msg_list.append(data)
        else:
            pass
        EventMap.send("weather_result_event", self.weather_msg_list)

    def request_weather_info(self, event=None, msg=None):
        state = poc.request_weather_info(0.0, 0.0)
        print("request_weather_info: {}".format(state))
        if not state:
            poc.request_weather_info(0.0, 0.0)

    def __poc_error_cb(self, params):
        PrintLog.log("PocService", "poc error: {}".format(params))
        self.error_msg = params[0]
        if self.error_msg == '帐号不存在' or self.error_msg == '登陆超时' or \
            self.error_msg == '帐号已在其他位置登录' or self.error_msg == '帐号信息已变更':
            EventMap.send("welcomescreen__check_error_reason", self.error_msg)
            self.error_msg = ""
            return
        if self.error_msg:
            pass

    def __poc_member_audio_enable_cb(self, params):
        self.__rocker_arm = params
        if self.__rocker_arm:
            pass
        else:
            pass
            # 您已被关闭发言

    def __set_ptt_hint_tone(self, event, msg):
        self.__ptt_hint_tone = msg
        EventMap.send("persistent_config_store", {"ptt_hint_tone": self.__ptt_hint_tone})  
        self.__ptt_tone_switch()  

    def __ptt_tone_switch(self):
        poc.Set_Tone_Switch(1 - self.__ptt_hint_tone)   # __ptt_hint_tone的值和Tone是反着的, 所以通过1-来取反

    def __get_rocker_arm(self, event, msg):
        return self.__rocker_arm

    def __set_account(self, event, msg):
        EventMap.send("persistent_config_store", {"account": msg})  

    def __set_password(self, event, msg):
        EventMap.send("persistent_config_store", {"password": msg})      

    def __get_platform(self, event, mode):
        return self.__platform

    def __set_platform(self, event=None, mode=None):
        pass

    def __check_xin_platform(self, event, msg):
        buf = bytearray(10)
        length = SecureData.Read(8, buf, 10)
        if -2 == length or -1 == length:
            return
        self.__platform_xin = buf[:length].decode('utf-8')
        if 1 == self.__platform and 'xin' == self.__platform_xin:
            EventMap.send("welcomescreen__check_error_reason", '已被芯平台绑定')
            EventMap.send("welcomescreen__check_cloud_status", 2)

    def __get_audio_status(self, event, msg):
        return poc.get_audiostate()

    def __securedata_xin_store(self):
        if self.__platform_dict.get(self.__platform) == 'xin':
            SecureData.Store(8, 'xin', 3)

    def __securedata_xin_clear(self):
        buf = bytearray(10)
        SecureData.Store(8, buf, 10)

    def __init_cb(self, msg):
        pass
        pass


    def __error_ptt_handler(self, params):
        """
        主要处理, 呼叫抢麦存在的异常, 并回滚处理一些操作
        """
        EventMap.send("ptt_battery_state", 0)
        if self.__session_info:
            session_info = self.__session_info
        else:
            if not self.__rocker_arm:
                session_info = "您已被关闭发言"
        if params[0] == self.BND_LISTEN_STOP or params[0] == self.BND_SPEAK_STOP or self.error_msg:
            # 判断是否call状态结束
            if params[0] == self.BND_LISTEN_STOP:
                EventMap.send("poc_play_status", False)
                EventMap.send("close_msgbox")
                EventMap.send("menubar__update_poc_status", 0)
            if params[0] == self.BND_SPEAK_STOP and self.main_call_end_state == self.CALL_STATE.IN_CALL:
                EventMap.send("poc_play_status", False)
                EventMap.send("close_msgbox")
                EventMap.send("menubar__update_poc_status", 0)
                self.main_call_end_state = self.CALL_STATE.CALL_END
        if self.error_msg:
            self.error_msg = ""
        self.last_audio = params[0]    
        EventMap.send("pocservice__call_member_status", 0)

    def __get_login_status(self, event, msg):
        return self.__login_status

    def __tts_play(self, event, msg):
        poc.play_tts(*msg)

    def __get_speaker_status(self, event, msg):
        return self.__speaker_status

    def __speaker_enable(self, event, msg=None):
        # 开启Poc对讲
        PrintLog.log("PocService", "speaker enable: {}".format(msg))
        if msg:
            EventMap.send("poc_play_status", True)  # 唤醒LCD
            if self.__speaker_status:
                EventMap.send("mediaservice__noise_reduction_enable", 1)
                poc.speak(1)
                if self.net_error:
                    if 3 != EventMap.send("welcomescreen__get_net_status"):
                        EventMap.send("mediaservice__tts_play", ("请更换卡", 1)) 
                        EventMap.send("load_msgbox", "请更换sim卡")  
                    return False
                
                # 检测当前群组
                curr_group = poc.group_getbyid(0)
                if -1 == curr_group:
                    EventMap.send("mediaservice__tts_play", (self.__group_name_default, 1)) 
                    EventMap.send("load_msgbox", self.__group_name_default)
                else:
                    if not self.__rocker_arm:
                        # EventMap.send("group", "您已被关闭发言")
                        EventMap.send("update_session_info", "您已被关闭发言")
                    else:
                        EventMap.send("load_msgbox", "讲话中...")
                        EventMap.send("menubar__update_poc_status", 1)
                        
            else:
                EventMap.send("mediaservice__audio_tone")
            return True
        # 关闭Poc对讲
        else:
            if self.__speaker_status:
                EventMap.send("mediaservice__noise_reduction_enable", 0)
                poc.speak(0)
                utime.sleep_ms(100)
                # group_name = self.__get_group_name()
                user_info = self.__get_user_info()
                if not self.__rocker_arm:
                    # EventMap.send("update_session_info", "{}(您已被关闭发言)".format(user_info))
                    pass
                else:
                    # EventMap.send("update_session_result", "Speaking")
                    EventMap.send("close_msgbox")
                    EventMap.send("menubar__update_poc_status", 0)
                    EventMap.send("poc_play_status", False)

    def __close_speaker(self, event, msg):
        utime.sleep(7)
        EventMap.send("mediaservice__tts_play", ("您已被关闭发言", 1))

    def get_member(self):
        return poc.member_getbyid(0)
    
    def __about_user(self, event=None, msg=None):
        """
        获取用户名称
        :param event:
        :param msg:
        :return:
        """
        if not self._user:
            self._user = self.get_member()[1]
        return self._user

    def __get_group_name(self, event=None, msg=None):
        if not self.__group_name:
            group = poc.group_getbyid(0)
            if isinstance(group, list):
                self.__group_name = group[1]
        if not self.__group_name:
            self.__group_name = self.__group_name_default
        return self.__group_name
    
    def __get_group_list(self, event=None, msg=None):
        """
        获取分组列表信息
        :param event:
        :param msg:
        :return:
        """
        group_count = poc.get_groupcount()
        group_list = poc.get_grouplist(0, group_count)
        return group_count, group_list

    def __get_member_list(self, event=None, msg=None):
        """获取成员列表"""
        group = poc.group_getbyid(0)
        if -1 == group:
            return -1, None
        member_count = poc.get_membercount(group[0])
        if -1 == member_count or 0 == member_count:
            return -1, None
        member_list = poc.get_memberlist(group[0], 0, member_count)
        return member_count, member_list

    def __get_group_count(self, event=None, msg=None):
        """
        获取组群总数事件
        :param event:
        :param msg:
        :return:
        """
        return poc.get_groupcount()
    
    def __get_group_online_count(self, event=None, msg=None):
        member_count, member_list = self.__get_member_list()
        if -1 == member_count:
            return 0
        total = 0 
        for each in (member_list):
            if each[2] == 3:
                total += 1
            else:
                return total
        return total

    def __join_group(self, event, msg):
        poc.joingroup(msg)

    def __leave_group(self, event, msg):
        poc.leavegroup() 

    def __call_member(self, event=None, msg=None):
        """
        呼叫成员事件
        :param event:
        :param msg:
        :return
        """
        call_sta = poc.callusers(msg, self.__calluser_callback)
        return call_sta
    
    def __calluser_callback(self, msg):
        """成员呼叫回调"""
        PrintLog("call user callback (msg) -> {}".format(msg))

    def __call_member_status(self, event, mode):
        '''
        检查设备是否在单呼状态

        mode: 1-PTT按下, 0-PTT抬起, 2-退出单呼返回群组
        '''
        if not self.__call_time_status:
            return
        if mode == PocService.PTT_ON:
            self.__call_member_timer.stop()
        elif mode == PocService.PTT_OFF:
            self.__call_member_timer.start(self.__call_quit_time * 1000, 0, lambda arg: self.__call_member_exit())
        else:
            self.__call_time_status = False
            poc.leavegroup()
            self.__call_member_timer.stop()

    def __call_member_exit(self, event=None, msg=None):
        '''
        退出单呼
        '''
        if not self.__call_time_status:
            return -1
        group = poc.group_getbyid(0)
        self.__call_time_status = False
        member_count = self.__get_member_count()
        if group and not group[-2]:
            return
        
        poc.leavegroup()
        if self.__get_user_info() == group[1]:
            return
        group = poc.group_getbyid(0)
        if member_count > 1 or group == -1:
            if self.__last_join_group:
                poc.joingroup(self.__last_join_group[0])

    def __get_member_count(self, event=None, msg=None):
        group = poc.group_getbyid(0)
        member_count = poc.get_membercount(group[0])
        return member_count

    def __get_user_info(self, event=None, msg=None):
        if not self.__user_info:
            self.__user_info = poc.member_getbyid(0)[1]
        return self.__user_info
    
    def __get_user_type(self, event, msg):
        group = poc.member_getbyid(0)
        if group[5]:
            return '(调度员)'
        return None

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




