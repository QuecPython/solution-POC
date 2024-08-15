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
from misc import USB
from machine import Pin, ExtInt

try:
    from common import AbstractLoad, EventMap, PrintLog
except:
    from usr.common import AbstractLoad, EventMap, PrintLog


class DevInfoService(AbstractLoad):
    def __init__(self):
        self.usb = USB()
        self.week_list = ["一","二","三","四","五","六","日"]

    def instance_after(self):
        EventMap.bind("devinfoservice__get_time", self.__get_time)
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


class MediaService(AbstractLoad):
    """
    媒体服务
    """
    def __init__(self):
        self.aud = audio.Audio(0)  # 0听筒 1耳机 2喇叭
        self.tts = audio.TTS(0)
        self.tts.setVolume(9)
        self.q = queue.Queue()
        
    def instance_after(self):
        EventMap.bind("mediaservice__audio_tone", self.__audio_tone)
        EventMap.bind("mediaservice__beep_tone", self.__beep_tone)
        EventMap.bind("mediaservice__tts_play", self.__tts_play)
        EventMap.bind("mediaservice__tts_stop", self.__tts_stop)
        poc.set_vol(1, 8)
        poc.set_vol(2, 1)

    def __beep_tone(self, event, msg):
        if self.q.empty():
            self.q.put(None)

    def __audio_tone(self, event, msg):
        self.aud.aud_tone_play(16, 100)

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
        self.__last_join_group = None
        self.net_error = False
        self.error_msg = ""
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
        self.__group_name_default = "当前无群组"

    def instance_after(self, *args, **kwargs):
        EventMap.bind("pocservice__speaker_enable", self.__speaker_enable)
        EventMap.bind("pocservice__close_speaker", self.__close_speaker)
        EventMap.bind("pocservice__set_ptt_hint_tone", self.__set_ptt_hint_tone)
        EventMap.bind("pocservice__join_group", self.__join_group)
        EventMap.bind("pocservice__leave_group", self.__leave_group)
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
        # 唤醒LCD
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
            if not self.__login_status:
                self.__login_status = True
            if self.tts_play_enable:
                EventMap.send("mediaservice__tts_play", (tts_msg, 1))
                if not self.__rocker_arm:
                    # 您已被关闭发言
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
        if param == 1:
            if 0 == poc.get_groupcount():
                self.__group_name = self.__group_name_default
        else:
            pass

    def __poc_request_lbs_info_cb(self, param):
        pass

    def __poc_weather_info_cb(self, param):
        pass

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

    def __poc_location_change_cb(self, params):
        pass

    def __poc_cell_location_change_cb(self, params):
        pass

    def __poc_member_audio_enable_cb(self, params):
        self.__rocker_arm = params
        if self.__rocker_arm:
            pass
        else:
            # 您已被关闭发言
            pass

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

    def upload_cell(self, *args):
        # ret = poc.send_gpsinfo(0.0, 0.0, list(utime.localtime()[:7]), 0.0, 0.0, 0.0)
        pass
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
                poc.speak(1)
                if self.net_error:
                    if 3 != EventMap.send("welcomescreen__get_net_status"):
                        EventMap.send("mediaservice__tts_play", ("请更换卡", 1)) 
                        EventMap.send("load_msgbox", "please replace the card.")  
                    return False
                
                # 检测当前群组
                curr_group = poc.group_getbyid(0)
                if -1 == curr_group:
                    EventMap.send("mediaservice__tts_play", (self.__group_name_default, 1)) 
                    EventMap.send("load_msgbox", self.__group_name_default)
                else:
                    if not self.__rocker_arm:
                        # 您已被关闭发言
                        EventMap.send("update_session_info", "您已被关闭发言")
                    else:
                        EventMap.send("load_msgbox", "Speaking...")
                        EventMap.send("menubar__update_poc_status", 1)
                        
            else:
                EventMap.send("mediaservice__audio_tone")
            return True
        # 关闭Poc对讲
        else:
            if self.__speaker_status:
                poc.speak(0)
                utime.sleep_ms(100)
                # group_name = self.__get_group_name()
                user_info = self.__get_user_info()
                if not self.__rocker_arm:
                    # 您已被关闭发言
                    pass
                else:
                    EventMap.send("close_msgbox")
                    EventMap.send("menubar__update_poc_status", 0)
                    EventMap.send("poc_play_status", False)

    def __close_speaker(self, event, msg):
        utime.sleep(7)
        EventMap.send("mediaservice__tts_play", ("您已被关闭发言", 1))

    def __get_group_name(self, event=None, msg=None):
        if not self.__group_name:
            group = poc.group_getbyid(0)
            if isinstance(group, list):
                self.__group_name = group[1]
        if not self.__group_name:
            self.__group_name = self.__group_name_default
        return self.__group_name

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






