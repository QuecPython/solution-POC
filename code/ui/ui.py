import osTimer
import utime
import sim
import net

try:
    from dev.lcd import ST7735
    from common import EventMap, AbstractLoad, Lock, PrintLog
    from styles import LVGLColor, FontStyle, CommonStyle, MainScreenStyle, DevInfoScreenStyle
except:
    from usr.dev.lcd import ST7735
    from usr.common import EventMap, AbstractLoad, Lock, PrintLog
    from usr.ui.styles import LVGLColor, FontStyle, CommonStyle, MainScreenStyle, DevInfoScreenStyle


import lvgl as lv


LCD_SIZE_WIDTH = 128
LCD_SIZE_HEIGHT = 160

g_lcd = ST7735()


def init_lvgl():
    lv.init()   # 初始化lvgl

    # Register SDL display driver.
    disp_buf1 = lv.disp_draw_buf_t()
    buf1_1 = bytearray(LCD_SIZE_WIDTH * LCD_SIZE_HEIGHT * 2)
    disp_buf1.init(buf1_1, None, len(buf1_1))
    disp_drv = lv.disp_drv_t()
    disp_drv.init()
    disp_drv.draw_buf = disp_buf1
    disp_drv.flush_cb = g_lcd._lcd.lcd_write
    disp_drv.hor_res = LCD_SIZE_WIDTH
    disp_drv.ver_res = LCD_SIZE_HEIGHT
    disp_drv.sw_rotate = 1
    disp_drv.rotated = lv.DISP_ROT._180
    disp_drv.register()
    lv.tick_inc(5)  # 启动lvgl线程


init_lvgl()


class Screen(AbstractLoad):
    class Type():
        Init = "init"
        Normal = "normal"   # 默认
        MenuBar = "menubar"
        ToolBar = "toolbar"
        StatusBar = "statusbar"

    def __init__(self):
        self.meta = None    # lvgl meta object
        self.meta_info = {}
        self.last_screen = None

    def set_last_screen(self, name):
        self.last_screen = name

    def load_before(self):
        pass

    def load(self):
        pass

    def load_after(self):
        pass

    def instance_after(self):
        pass

    def deactivate(self):
        pass
    
    def up_press(self):
        pass
    
    def down_press(self):
        pass

    def menu_press(self):
        pass

    def back_press(self):
        pass   

    def prev_idx(self, now_idx, count):
        cur_idx = now_idx - 1
        if cur_idx < 0:
            cur_idx = count - 1
        return cur_idx
    def next_idx(self, now_idx, count):
        cur_idx = now_idx + 1
        if cur_idx > count - 1:
            cur_idx = 0
        return cur_idx


# 屏幕栏, MenuBar, ToolBar, StatusBar
class MenuBar(AbstractLoad):
    NAME = "MenuBar"

    def __init__(self):
        self.menu_bar = None

        self.base_timer = osTimer()
        self.get_battery_timer = osTimer()
        self.get_signal_timer = osTimer()

    def instance_after(self):
        EventMap.bind("menubar__show", self.__show)
        EventMap.bind("menubar__flush", self.__flush)
        EventMap.bind("menubar__close", self.__close)

        # EventMap.bind("menubar__update_net_status", self.__update_net_status)
        EventMap.bind("menubar__update_poc_status", self.__update_poc_status)

    def __close(self, event=None, msg=None):
        if self.menu_bar is not None:
            self.menu_bar.delete()
            self.menu_bar = None

    def __show(self, event, meta):      
        self.__close()
            
        self.menu_bar = lv.obj(meta)
        self.menu_bar.set_pos(0, 0)
        self.menu_bar.set_size(128, 20)
        self.menu_bar.add_style(CommonStyle.container_bge1e1e1, lv.PART.MAIN | lv.STATE.DEFAULT)
        self.menu_bar.set_style_pad_left(0, 0)
        self.menu_bar.set_style_pad_right(0, 0)
        self.menu_bar.set_style_pad_top(0, 0)

        self.img_signal = lv.img(self.menu_bar)
        self.img_signal.set_src("U:/img/signal_0.png")
        self.img_signal.set_size(13, 13)
        self.img_signal.set_pivot(0, 0)
        self.img_signal.set_angle(0)
        self.img_signal.add_style(CommonStyle.img_style, lv.PART.MAIN | lv.STATE.DEFAULT)
        self.img_signal.align(lv.ALIGN.LEFT_MID, 5, 0)
        self.lab_signal = lv.label(self.menu_bar)
        self.lab_signal.set_text("x")
        self.lab_signal.align(lv.ALIGN.LEFT_MID, 20, 0)
        self.lab_signal.add_style(FontStyle.consolas_12_txt000000_bg2195f6, lv.PART.MAIN | lv.STATE.DEFAULT)
        net_status = EventMap.send("netservice__get_net_generation")
        if net_status:
            self.img_signal.set_src("U:/img/signal_5.png")
            self.lab_signal.set_text(net_status)
        
        self.img_poc = lv.img(self.menu_bar)
        # self.img_poc.set_src("U:/img/poc_speaking.png") # poc_play
        self.img_poc.set_size(13, 13)
        self.img_poc.set_pivot(0, 0)
        self.img_poc.set_angle(0)
        self.img_poc.add_style(CommonStyle.img_style, lv.PART.MAIN | lv.STATE.DEFAULT)
        self.img_poc.align(lv.ALIGN.LEFT_MID, 35, 0)

        self.img_gps = lv.img(self.menu_bar)
        # self.img_gps.set_src("U:/img/gps.png")
        self.img_gps.set_size(13, 13)
        self.img_gps.set_pivot(0, 0)
        self.img_gps.set_angle(0)
        self.img_gps.add_style(CommonStyle.img_style, lv.PART.MAIN | lv.STATE.DEFAULT)
        self.img_gps.align(lv.ALIGN.RIGHT_MID, -65, 0)


        self.img_battery = lv.img(self.menu_bar)
        # self.img_battery.set_src("U:/img/battery_4.png")
        # self.img_battery.set_size(21, 16)
        self.img_battery.set_src("U:/img/charge_battery.png")
        self.img_battery.set_size(13, 13)
        self.img_battery.set_pivot(0, 0)
        self.img_battery.set_angle(0)
        self.img_battery.add_style(CommonStyle.img_style, lv.PART.MAIN | lv.STATE.DEFAULT)
        self.img_battery.align(lv.ALIGN.RIGHT_MID, -27, 0)
        self.lab_battery = lv.label(self.menu_bar)
        self.lab_battery.set_text("100%")
        self.lab_battery.align(lv.ALIGN.RIGHT_MID, -2, 0)
        self.lab_battery.add_style(FontStyle.consolas_12_txt000000_bg2195f6, lv.PART.MAIN | lv.STATE.DEFAULT)
        
        self.lab_time = lv.label(self.menu_bar)
        self.lab_time.set_text("")
        self.lab_time.align(lv.ALIGN.CENTER, 0, 0)
        self.lab_time.add_style(FontStyle.consolas_12_txt000000_bg2195f6, lv.PART.MAIN | lv.STATE.DEFAULT)

        self.__update_time()
        self.__update_battery()
        self.__update_signal()
        self.base_timer.start(1000 * 30, 1, self.__update_time)
        self.get_battery_timer.start(10000, 1, self.__update_battery)
        self.get_signal_timer.start(2000, 1, self.__update_signal)

        EventMap.bind("menubar__update_gps_status", self.__update_gps_status)
        

    def __flush(self, event, msg):
        pass

    def __update_time(self, arg=None):
        time = EventMap.send("devinfoservice__get_time")
        if time:
            self.lab_time.set_text(time[1])

    def __update_battery(self, arg=None):
        battery = EventMap.send("screen_get_battery")
        if battery:
            self.img_battery.set_src(battery)

    def __update_signal(self, arg=None):
        sig = EventMap.send("screen_get_signal")
        if 0 < sig <= 31:
            self.img_signal.set_src('U:/img/signal_' + str(int(sig * 5 / 31)) + '.png')
            self.lab_signal.set_text("4G")
        else:
            self.img_signal.set_src("U:/img/signal_0.png")
            self.lab_signal.set_text("x")
            
    def __update_poc_status(self, event, msg):
        """
        0 停止  1 对讲  2 播放
        """
        PrintLog.log(MenuBar.NAME, "poc status: {}".format(msg))
        if 0 == msg:
            self.img_poc.add_flag(lv.obj.FLAG.HIDDEN)
        elif 1 == msg:
            self.img_poc.clear_flag(lv.obj.FLAG.HIDDEN)
            self.img_poc.set_src("U:/img/poc_speaking.png")
        elif 2 == msg:
            self.img_poc.clear_flag(lv.obj.FLAG.HIDDEN)
            self.img_poc.set_src("U:/img/poc_play.png")

    def __update_gps_status(self, event, msg):
        print("__update_gps_status -----------------  {}".format(msg))
        if not msg:
            self.img_gps.add_flag(lv.obj.FLAG.HIDDEN)
        else:
            self.img_gps.clear_flag(lv.obj.FLAG.HIDDEN)
            self.img_gps.set_src("U:/img/gps.png")


class ToolBar():
    pass


class StatusBar():
    pass


# 消息框
class PromptBox(AbstractLoad):
    NAME = "PromptBox"

    def __init__(self):
        self.prompt_box = None
        self.prompt_label = None
        self.prompt_box = None

    def instance_after(self):
        EventMap.bind("promptbox__show", self.__show)
        EventMap.bind("promptbox__close", self.__close)

    def __close(self, event=None, msg=None):
        if self.prompt_box is not None:
            self.prompt_box.delete()
            self.prompt_box = None

    def __show(self, event, msg):
        if self.prompt_box is not None:
            self.prompt_box.delete()
            self.prompt_box = None

        meta = msg.get("meta")
        show_msg = msg.get("msg")

        self.prompt_box = lv.msgbox(meta, "Prompt", "", [], False)
        self.prompt_box.set_size(98, 80)
        self.prompt_box.align(lv.ALIGN.CENTER, 0, 0)
        self.prompt_label = lv.label(self.prompt_box)
        self.prompt_label.set_pos(0, 0)
        self.prompt_label.set_size(70, 60)
        self.prompt_label.add_style(FontStyle.consolas_12_txt000000_bg2195f6, lv.PART.MAIN | lv.STATE.DEFAULT)
        self.prompt_label.set_text(show_msg)
        self.prompt_label.set_long_mode(lv.label.LONG.WRAP)
        self.prompt_label.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)                         


# UI屏幕
class MainScreen(Screen):
    NAME = "MainScreen"

    def __init__(self):
        self.meta = lv.obj()    # lvgl meta object

        self.btn_list = []
        self.btn_list_name = ["群组管理", "成员列表", "设备信息", "天气", "设置"]
        self.curr_idx = 0
        self.count = len(self.btn_list_name)


    def load_before(self):
        EventMap.send("request_weather_info", None)

    def load(self):
        self.meta.add_style(CommonStyle.default, lv.PART.MAIN | lv.STATE.DEFAULT)
        # 列表------------------------------------------------------------------------------------------
        self.list_menu = lv.list(self.meta)
        self.list_menu.set_pos(0, 20)
        self.list_menu.set_size(128, 140)
        self.list_menu.set_style_pad_left(0, 0)
        self.list_menu.set_style_pad_right(0, 0)
        self.list_menu.set_style_pad_top(0, 0)
        self.list_menu.set_style_pad_row(1, 0)
        self.list_menu.add_style(CommonStyle.container_bgffffff, lv.PART.MAIN | lv.STATE.DEFAULT)
        self.list_menu.add_style(MainScreenStyle.list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.DEFAULT)
        self.list_menu.add_style(MainScreenStyle.list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.SCROLLED)
        
        # 添加管理列表------------------------------------------------------------------------------------------
        self.btn_list = []
        for idx, item in enumerate(self.btn_list_name):
            btn = lv.btn(self.list_menu)
            btn.set_pos(20, 0)
            btn.set_size(128, 34)
            btn.add_style(MainScreenStyle.btn_group, lv.PART.MAIN | lv.STATE.DEFAULT)
            img = lv.img(btn)
            img.align(lv.ALIGN.LEFT_MID, 10, 0)
            img.set_size(32, 32)
            img.set_src('U:/img/main_list_{}.png'.format(idx + 1))
            lab = lv.label(btn)
            lab.align(lv.ALIGN.LEFT_MID, 50, 10)
            lab.set_size(128, 30)
            lab.set_text(item)
            self.btn_list.append((btn, img, lab))
        self.add_state()


    def load_after(self):
        pass

    def add_state(self):
        currBtn = self.list_menu.get_child(self.curr_idx)
        currBtn.set_style_bg_color(lv.color_make(0xe6, 0x94, 0x10), lv.PART.MAIN | lv.STATE.DEFAULT)
        currBtn.set_style_bg_grad_color(lv.color_make(0xe6, 0x94, 0x10), lv.PART.MAIN | lv.STATE.DEFAULT)
        self.btn_list[self.curr_idx][2].set_long_mode(lv.label.LONG.SCROLL_CIRCULAR)
        currBtn.scroll_to_view(lv.ANIM.OFF)
        
    def clear_state(self):
        currBtn = self.list_menu.get_child(self.curr_idx)
        currBtn.set_style_bg_color(LVGLColor.BASE_COLOR_WHITE, lv.PART.MAIN | lv.STATE.DEFAULT)
        currBtn.set_style_bg_grad_color(LVGLColor.BASE_COLOR_WHITE, lv.PART.MAIN | lv.STATE.DEFAULT)
        self.btn_list[self.curr_idx][2].set_long_mode(lv.label.LONG.SCROLL_CIRCULAR)
        currBtn.scroll_to_view(lv.ANIM.OFF)

    def up_press(self):
        """
        作为滚动按键
        """
        self.clear_state()
        self.curr_idx = self.prev_idx(self.curr_idx, self.count)
        self.add_state()
        
    def down_press(self):
        """
        作为滚动按键
        """
        self.clear_state()
        self.curr_idx = self.next_idx(self.curr_idx, self.count)
        self.add_state()

    def menu_press(self):
        """
        作为点击按键
        """
        if self.curr_idx == 0:
            screen = "GroupScreen"
        elif self.curr_idx == 1:
            screen = "MemberScreen"
        elif self.curr_idx == 2:
            screen = "DeviceScreen"
        elif self.curr_idx == 3:
            screen = "WeatherScreen"
        elif self.curr_idx == 4:
            screen = "SettingScreen"
        else:
            return
        EventMap.send("load_screen", {"screen": screen})


class WelcomeScreen(Screen):
    NAME = "WelcomeScreen"

    def __init__(self):
        self.meta = lv.obj()    # lvgl meta object  
        self.main_screen_timer = osTimer()
        self.check_net_timer = osTimer()
        self.check_xin_timer = osTimer()
        self.net_status = 0
        self.cloud_status = 0
        self.connect_field_count = 0
        self.connect_switch = False
        self.error_reason = None

    def load(self):
        self.msgbox_tip = lv.msgbox(self.meta, "Tip:", "", [], False)
        self.msgbox_tip.set_size(98, 80)
        self.msgbox_tip.align(lv.ALIGN.CENTER, 0, 0)
        self.lab_msgboxtip = lv.label(self.msgbox_tip)
        self.lab_msgboxtip.set_size(88, 40)
        self.lab_msgboxtip.set_text("初始化中...")
        self.lab_msgboxtip.set_long_mode(lv.label.LONG.SCROLL_CIRCULAR)
        self.lab_msgboxtip.add_style(FontStyle.consolas_12_txt000000_bg2195f6, lv.PART.MAIN | lv.STATE.DEFAULT)
        self.lab_msgboxtip.set_style_text_align(lv.TEXT_ALIGN.LEFT, 0)
        self.lab_msgboxtip.align(lv.ALIGN.CENTER, 0, 0)
        EventMap.bind("welcomescreen__net_status", self.__net_status)
        EventMap.bind("welcomescreen__get_net_status", self.__get_net_status)
        EventMap.bind("welcomescreen__check_cloud_status", self.__check_cloud_status)
        EventMap.bind("welcomescreen__check_error_reason", self.__check_error_reason)
        count = 0
        while True:
            if 1 == sim.getStatus():
                break
            utime.sleep(1)
            count += 1
            if count > 6:
                break
        if 0 == sim.getStatus():
            self.net_status = 1   # 未插卡标志 
            self.lab_msgboxtip.set_text("未检测到sim卡")
            EventMap.send("mediaservice__tts_play", ("未检测到sim卡", 0))
        else:
            self.lab_msgboxtip.set_text("网络注册中...")
            self.check_net_timer.start(40 * 1000, 0, lambda arg: self.__check_net_status())
            self.check_xin_timer.start(20 * 1000, 0, lambda arg: self.__check_xin_result())

    def __check_xin_result(self):
        EventMap.send("pocservice__check_xin_platform")
        if self.error_reason == "已被芯平台绑定":
            self.check_net_timer.stop()
            self.lab_msgboxtip.set_text("已被芯平台绑定")
            EventMap.send("mediaservice__tts_play", (self.error_reason, 0))

    def __net_status(self, event, msg):
        self.net_status = msg

    def __get_net_status(self, event, msg):
        return self.net_status

    def __check_cloud_status(self, event, msg):
        self.cloud_status = msg
        if self.cloud_status == 2:
            self.__check_net_status()
        if self.cloud_status == 1:
            self.check_xin_timer.stop()
            self.check_net_timer.stop() # /
            self.error_reason = None
            # 3s 之后跳转主界面
            self.main_screen_timer.start(3*1000, 0, lambda arg: EventMap.send("load_screen", {"screen": MainScreen.NAME}))
            # EventMap.send_stop("blink_led")  # 停止闪烁LED

    def __check_error_reason(self, event, msg):
        self.error_reason = msg

    def __check_net_status(self):
        # PrintLog.log(WelcomeScreen.NAME, "check net status: {} , cloud_status {}".format(self.net_status, self.cloud_status))
        if self.cloud_status == 1:
            return
        if self.net_status == 2 and self.cloud_status == 1:
            return
        if self.error_reason is not None:
            self.check_xin_timer.stop()
            reason = self.error_reason  
        elif self.net_status == 3:
            self.check_xin_timer.stop()
            reason = "网络异常"
        elif self.net_status == 2 and self.cloud_status != 1:
            reason = "账号登录中..."
        else:
            reason = "网络搜索中..."
        if "帐号不存在" == reason:
            self.lab_msgboxtip.set_text("账号不存在")
            EventMap.send("mediaservice__tts_play", (reason, 0))
        else:
            self.lab_msgboxtip.set_text(reason)


class MemberScreen(Screen):
    NAME = "MemberScreen"

    def __init__(self):
        super().__init__()
        self.cur = 0
        self.count = 6

        self.btn_list = []
        self.curr_idx = 0
        self.member_check_cur_list = list()
        self.member_btn_list = list()
        self.member_list = list()
        self.count = len(self.member_btn_list)
        self.member_update_flag = True

        self.msgbox_close_time = 2
        self.msgbox_close_timer = osTimer()

        self.meta = lv.obj()    # lvgl meta object

        self.meta.add_style(CommonStyle.default, lv.PART.MAIN | lv.STATE.DEFAULT)

        # 列表------------------------------------------------------------------------------------------
        self.list_menu = lv.list(self.meta)

    def load_before(self):
        EventMap.bind("get_member_check_list", self.__get_member_check_list)
        EventMap.bind("send_select_member_list", self.__send_select_member_list)
        EventMap.bind("update_member_info", self.update_member_info)

    def load(self):
        self.__load_member_list()
        self.__member_screen_list_create()
        self.__load_group_cur()
        if self.member_list is None or self.member_list == -1 or not len(self.member_list):
            EventMap.send("load_msgbox", "此群组无成员")
            return False
        if self.cur >= 0:
            self.clear_state()
        self.cur = 0
        self.add_state()

    def add_state(self):    # 添加选中状态
        currBtn = self.list_menu.get_child(self.curr_idx)
        currBtn.set_style_bg_color(lv.color_make(0xe6, 0x94, 0x10), lv.PART.MAIN | lv.STATE.DEFAULT)
        currBtn.set_style_bg_grad_color(lv.color_make(0xe6, 0x94, 0x10), lv.PART.MAIN | lv.STATE.DEFAULT)
        self.btn_list[self.curr_idx][2].set_long_mode(lv.label.LONG.SCROLL_CIRCULAR)
        currBtn.scroll_to_view(lv.ANIM.OFF)
        
    def clear_state(self):  # 清除选中状态
        currBtn = self.list_menu.get_child(self.curr_idx)
        currBtn.set_style_bg_color(LVGLColor.BASE_COLOR_WHITE, lv.PART.MAIN | lv.STATE.DEFAULT)
        currBtn.set_style_bg_grad_color(LVGLColor.BASE_COLOR_WHITE, lv.PART.MAIN | lv.STATE.DEFAULT)
        self.btn_list[self.curr_idx][2].set_long_mode(lv.label.LONG.SCROLL_CIRCULAR)
        currBtn.scroll_to_view(lv.ANIM.OFF)
        
    def up_press(self):
        """
        作为滚动按键
        """
        self.clear_state()
        self.curr_idx = self.prev_idx(self.curr_idx, self.count)
        self.add_state()

    def down_press(self, event=None, msg=None):
        self.clear_state()
        self.curr_idx = self.next_idx(self.curr_idx, self.count)
        self.add_state()
        
    def menu_press(self, event=None, msg=None):
        pass

    def back_press(self, event=None, msg=None):
        EventMap.send("close_msgbox")
        EventMap.send("load_screen", {"screen": "MainScreen"})
        if self.curr_idx > 0:
            self.clear_state()
            self.curr_idx = 0

    def __get_member_check_list(self, topic=None, mode=None):
        if self.member_check_cur_list:
            return True
        else:
            return False
        
    def __send_select_member_list(self, topic=None, mode=None):
        self.cur = 0
        self.member_update_flag = True
        send_list = []
        for i in self.member_check_cur_list:
            send_list.append(self.member_list[i][0])
        # EventMap.send("member_speakbtn_click", send_list)
        # EventMap.send("load_screen", {"screen": "MainScreen"})
        # self.__clear_member_img_state()

    def __clear_member_img_state(self):
        if self.member_check_cur_list:
            for i in self.member_check_cur_list:
                member_state = self.member_list[i][2]
                if member_state == 1:
                    img_path_name = "U:/img/member_online.png"
                else:
                    img_path_name = "U:/img/member_onlines.png"
                self.member_btn_list[i][0].set_src(img_path_name)
            self.member_check_cur_list = []

    def update_member_info(self, event, mode):
        self.member_update_flag = True

    def __load_member_list(self):
        if not self.member_update_flag:
            return
        else:
            response = EventMap.send("member_get_list")
            print(response)
            if response:
                self.count, self.member_list = response

    def __member_screen_list_create(self):
        """成员界面列表重新创建"""
        # 把之前的list删掉
        if self.member_update_flag:
            self.list_menu.delete()
            # 再创建list
            self.list_menu = lv.list(self.meta)
            self.list_menu.set_pos(0, 20)
            self.list_menu.set_size(128, 140)
            self.list_menu.set_style_pad_left(0, 0)
            self.list_menu.set_style_pad_right(0, 0)
            self.list_menu.set_style_pad_top(0, 0)
            self.list_menu.set_style_pad_row(1, 0)
            self.list_menu.add_style(CommonStyle.container_bgffffff, lv.PART.MAIN | lv.STATE.DEFAULT)
            self.list_menu.add_style(MainScreenStyle.list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.DEFAULT)
            self.list_menu.add_style(MainScreenStyle.list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.SCROLLED)
            if self.count:
                # 根据从poc_main接收的member列表往member_screen_list
                self.add_member_msg(0, self.count)
                self.member_update_flag = False
            else:
                # 无成员信息弹窗提示
                EventMap.send("load_msgbox", "无成员")

    def add_member_msg(self, index, end):
        self.member_btn_list = []
        for each in self.member_list[index:end]:
            btn = lv.btn(self.list_menu)
            btn.set_pos(20, 0)
            btn.set_size(128, 34)
            btn.add_style(MainScreenStyle.btn_group, lv.PART.MAIN | lv.STATE.DEFAULT)
            img = lv.img(btn)
            img.align(lv.ALIGN.LEFT_MID, 10, 0)
            img.set_size(32, 32)
            img.set_src('U:/img/number_{}.png'.format(each[4] + 1))
            lab = lv.label(btn)
            lab.align(lv.ALIGN.LEFT_MID, 50, 10)
            lab.set_size(128, 30)
            lab.set_text(each[1])
            self.btn_list.append((btn, img, lab))
        self.add_state()

    def __load_group_cur(self):
        ret = EventMap.send("get_group_name")
        if ret:
            print(ret)
            EventMap.send("load_msgbox", '当前群组: {}'.format(ret))
            self.msgbox_close_timer.start(self.msgbox_close_time * 1000, 0, lambda arg: EventMap.send("close_msgbox"))


class GroupScreen(Screen):
    NAME = "GroupScreen"

    def __init__(self):
        super().__init__()
        self.cur = 0
        self.count = 6
        self.current_button = None

        self.btn_list = []
        self.group_list = list()
        self.curr_idx = 0
        self.group_update_flag = True
        self.group_bottom_name = None

        self.msgbox_close_time = 2
        self.msgbox_close_timer = osTimer()

        self.meta = lv.obj()    # lvgl meta object

        self.meta.add_style(CommonStyle.default, lv.PART.MAIN | lv.STATE.DEFAULT)

        # 列表------------------------------------------------------------------------------------------
        self.list_menu = lv.list(self.meta)

    def load_before(self):
        EventMap.bind("update_group_info", self.__update_group_info)

    def load(self):
        self.__load_group_list()
        self.__group_screen_list_create()
        self.__load_group_cur()
        if self.group_list is None or self.group_list == -1 or not len(self.group_list):
            EventMap.send("load_msgbox", "未加入群组")
            return False
        if self.cur >= 0:
            self.clear_state()
        self.cur = 0
        self.add_state()
        
    def add_state(self):    # 添加选中状态
        currBtn = self.list_menu.get_child(self.curr_idx)
        currBtn.set_style_bg_color(lv.color_make(0xe6, 0x94, 0x10), lv.PART.MAIN | lv.STATE.DEFAULT)
        currBtn.set_style_bg_grad_color(lv.color_make(0xe6, 0x94, 0x10), lv.PART.MAIN | lv.STATE.DEFAULT)
        self.btn_list[self.curr_idx][2].set_long_mode(lv.label.LONG.SCROLL_CIRCULAR)
        currBtn.scroll_to_view(lv.ANIM.OFF)
        
    def clear_state(self):  # 清除选中状态
        currBtn = self.list_menu.get_child(self.curr_idx)
        currBtn.set_style_bg_color(LVGLColor.BASE_COLOR_WHITE, lv.PART.MAIN | lv.STATE.DEFAULT)
        currBtn.set_style_bg_grad_color(LVGLColor.BASE_COLOR_WHITE, lv.PART.MAIN | lv.STATE.DEFAULT)
        self.btn_list[self.curr_idx][2].set_long_mode(lv.label.LONG.SCROLL_CIRCULAR)
        currBtn.scroll_to_view(lv.ANIM.OFF)
    
    def up_press(self):
        """
        作为滚动按键
        """
        self.clear_state()
        self.curr_idx = self.prev_idx(self.curr_idx, self.count)
        self.add_state()

    def down_press(self, event=None, msg=None):
        self.clear_state()
        self.curr_idx = self.next_idx(self.curr_idx, self.count)
        self.add_state()
        
    def menu_press(self, event=None, msg=None):
        pass

    def back_press(self, event=None, msg=None):
        EventMap.send("close_msgbox")
        EventMap.send("load_screen", {"screen": "MainScreen"})
        if self.curr_idx > 0:
            self.clear_state()
            self.curr_idx = 0

    def __update_group_info(self, event, mode):
        # 更新群组
        self.group_update_flag = True

    def __load_group_list(self):
        if not self.group_update_flag:
            return
        response = EventMap.send("group_get_list")
        # 判断是否获取到组群列表
        # print(response)
        if response:
            self.count, self.group_list = response

    def __group_screen_list_create(self):
        """组群界面列表重新创建"""
        # 把之前的list删掉
        if self.group_update_flag:
            self.list_menu.delete()
            # 再创建list
            self.list_menu = lv.list(self.meta)
            self.list_menu.set_pos(0, 20)
            self.list_menu.set_size(128, 140)
            self.list_menu.set_style_pad_left(0, 0)
            self.list_menu.set_style_pad_right(0, 0)
            self.list_menu.set_style_pad_top(0, 0)
            self.list_menu.set_style_pad_row(1, 0)
            self.list_menu.add_style(CommonStyle.container_bgffffff, lv.PART.MAIN | lv.STATE.DEFAULT)
            self.list_menu.add_style(MainScreenStyle.list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.DEFAULT)
            self.list_menu.add_style(MainScreenStyle.list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.SCROLLED)
            if self.count:
                # 根据从poc_main接收的group列表往group_list
                self.add_group_msg(0, self.count)
                self.group_update_flag = False
            else:
                # 无组群信息弹窗提示
                # print("No group found")
                EventMap.send("load_msgbox", "无群组")

    def add_group_msg(self, index, end):
        self.btn_list = []
        for each in self.group_list[index:end]:
            btn = lv.btn(self.list_menu)
            btn.set_pos(20, 0)
            btn.set_size(128, 34)
            btn.add_style(MainScreenStyle.btn_group, lv.PART.MAIN | lv.STATE.DEFAULT)
            img = lv.img(btn)
            img.align(lv.ALIGN.LEFT_MID, 10, 0)
            img.set_size(32, 32)
            img.set_src('U:/img/number_{}.png'.format(each[3] + 1))
            lab = lv.label(btn)
            lab.align(lv.ALIGN.LEFT_MID, 50, 10)
            lab.set_size(128, 30)
            lab.set_text(each[1])
            lab.add_style(FontStyle.consolas_12_txt000000_bg2195f6, lv.PART.MAIN | lv.STATE.DEFAULT)
            self.btn_list.append((btn, img, lab))
        self.add_state()

    def __load_group_cur(self):
        ret = EventMap.send("get_group_name")
        if ret:
            print(ret)
            EventMap.send("load_msgbox", '当前群组: {}'.format(ret))
            self.msgbox_close_timer.start(self.msgbox_close_time * 1000, 0, lambda arg: EventMap.send("close_msgbox"))


class SettingScreen(Screen):
    NAME = "SettingScreen"

    def __init__(self):
        super().__init__()
        self.meta = lv.obj()    # lvgl meta object

        self.btn_list = []
        self.btn_list_name = ["关于本机", "壁纸"]
        self.curr_idx = 0
        self.count = len(self.btn_list_name)

    def load(self):
        self.meta.add_style(CommonStyle.default, lv.PART.MAIN | lv.STATE.DEFAULT)

        # 列表------------------------------------------------------------------------------------------
        self.list_menu = lv.list(self.meta)
        self.list_menu.set_pos(0, 20)
        self.list_menu.set_size(128, 140)
        self.list_menu.set_style_pad_left(0, 0)
        self.list_menu.set_style_pad_right(0, 0)
        self.list_menu.set_style_pad_top(0, 0)
        self.list_menu.set_style_pad_row(1, 0)
        self.list_menu.add_style(CommonStyle.container_bgffffff, lv.PART.MAIN | lv.STATE.DEFAULT)
        self.list_menu.add_style(MainScreenStyle.list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.DEFAULT)
        self.list_menu.add_style(MainScreenStyle.list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.SCROLLED)
		
		# 添加管理列表------------------------------------------------------------------------------------------
        self.btn_list = []
        for idx, item in enumerate(self.btn_list_name):
            btn = lv.btn(self.list_menu)
            btn.set_pos(20, 0)
            btn.set_size(128, 34)
            btn.add_style(MainScreenStyle.btn_group, lv.PART.MAIN | lv.STATE.DEFAULT)
            img = lv.img(btn)
            img.align(lv.ALIGN.LEFT_MID, 10, 0)
            img.set_size(32, 32)
            img.set_src('U:/img/number_{}.png'.format(idx + 1))
            lab = lv.label(btn)
            lab.align(lv.ALIGN.LEFT_MID, 50, 10)
            lab.set_size(128, 30)
            lab.set_text(item)
            self.btn_list.append((btn, img, lab))
        self.add_state()

    def add_state(self):    # 添加选中状态
        currBtn = self.list_menu.get_child(self.curr_idx)
        currBtn.set_style_bg_color(lv.color_make(0xe6, 0x94, 0x10), lv.PART.MAIN | lv.STATE.DEFAULT)
        currBtn.set_style_bg_grad_color(lv.color_make(0xe6, 0x94, 0x10), lv.PART.MAIN | lv.STATE.DEFAULT)
        self.btn_list[self.curr_idx][2].set_long_mode(lv.label.LONG.SCROLL_CIRCULAR)
        currBtn.scroll_to_view(lv.ANIM.OFF)
        
    def clear_state(self):  # 清除选中状态
        currBtn = self.list_menu.get_child(self.curr_idx)
        currBtn.set_style_bg_color(LVGLColor.BASE_COLOR_WHITE, lv.PART.MAIN | lv.STATE.DEFAULT)
        currBtn.set_style_bg_grad_color(LVGLColor.BASE_COLOR_WHITE, lv.PART.MAIN | lv.STATE.DEFAULT)
        self.btn_list[self.curr_idx][2].set_long_mode(lv.label.LONG.SCROLL_CIRCULAR)
        currBtn.scroll_to_view(lv.ANIM.OFF)
    
    def up_press(self):
        """
        作为滚动按键
        """
        self.clear_state()
        self.curr_idx = self.prev_idx(self.curr_idx, self.count)
        self.add_state()
        
    def down_press(self, event=None, msg=None):
        self.clear_state()
        self.curr_idx = self.next_idx(self.curr_idx, self.count)
        self.add_state()
        
    def menu_press(self, event=None, msg=None):
        pass
        
    def back_press(self, event=None, msg=None):
        EventMap.send("load_screen", {"screen": "MainScreen"})
        if self.curr_idx > 0:
            self.clear_state()
            self.curr_idx = 0


class WeatherScreen(Screen):
    NAME = "WeatherScreen"

    def __init__(self):
        super().__init__()
        self.meta = lv.obj()    # lvgl meta object
        
        self.btn_list = []
        self.btn_list_name = ["今天", "明天", "后天"]
        self.curr_idx = 0
        self.count = len(self.btn_list_name)

    def load(self):
        self.meta.add_style(CommonStyle.default, lv.PART.MAIN | lv.STATE.DEFAULT)
        # 列表------------------------------------------------------------------------------------------
        self.list_menu = lv.list(self.meta)
        self.list_menu.set_pos(0, 20)
        self.list_menu.set_size(128, 140)
        self.list_menu.set_style_pad_left(0, 0)
        self.list_menu.set_style_pad_right(0, 0)
        self.list_menu.set_style_pad_top(0, 0)
        self.list_menu.set_style_pad_row(1, 0)
        self.list_menu.add_style(CommonStyle.container_bgffffff, lv.PART.MAIN | lv.STATE.DEFAULT)
        self.list_menu.add_style(MainScreenStyle.list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.DEFAULT)
        self.list_menu.add_style(MainScreenStyle.list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.SCROLLED)
        
        # 添加管理列表------------------------------------------------------------------------------------------
        self.btn_list = []
        for idx, item in enumerate(self.btn_list_name):
            btn = lv.btn(self.list_menu)
            btn.set_pos(20, 0)
            btn.set_size(128, 34)
            btn.add_style(MainScreenStyle.btn_group, lv.PART.MAIN | lv.STATE.DEFAULT)
            img = lv.img(btn)
            img.align(lv.ALIGN.LEFT_MID, 10, 0)
            img.set_size(32, 32)
            img.set_src('U:/img/number_{}.png'.format(idx + 1))
            lab = lv.label(btn)
            lab.align(lv.ALIGN.LEFT_MID, 50, 10)
            lab.set_size(128, 30)
            lab.set_text(item)
            self.btn_list.append((btn, img, lab))
        self.add_state()

    def add_state(self):    # 添加选中状态
        currBtn = self.list_menu.get_child(self.curr_idx)
        currBtn.set_style_bg_color(lv.color_make(0xe6, 0x94, 0x10), lv.PART.MAIN | lv.STATE.DEFAULT)
        currBtn.set_style_bg_grad_color(lv.color_make(0xe6, 0x94, 0x10), lv.PART.MAIN | lv.STATE.DEFAULT)
        self.btn_list[self.curr_idx][2].set_long_mode(lv.label.LONG.SCROLL_CIRCULAR)
        currBtn.scroll_to_view(lv.ANIM.OFF)

    def clear_state(self):  # 清除选中状态
        currBtn = self.list_menu.get_child(self.curr_idx)
        currBtn.set_style_bg_color(LVGLColor.BASE_COLOR_WHITE, lv.PART.MAIN | lv.STATE.DEFAULT)
        currBtn.set_style_bg_grad_color(LVGLColor.BASE_COLOR_WHITE, lv.PART.MAIN | lv.STATE.DEFAULT)
        self.btn_list[self.curr_idx][2].set_long_mode(lv.label.LONG.SCROLL_CIRCULAR)
        currBtn.scroll_to_view(lv.ANIM.OFF)
        
    def up_press(self):
        """
        作为滚动按键
        """
        self.clear_state()
        self.curr_idx = self.prev_idx(self.curr_idx, self.count)
        self.add_state()

    def down_press(self, event=None, msg=None):
        self.clear_state()
        self.curr_idx = self.next_idx(self.curr_idx, self.count)
        self.add_state()
    
    def menu_press(self, event=None, msg=None):
        EventMap.send("load_screen", {"screen": "WeatherInfoScreen"})
        
    def back_press(self, event=None, msg=None):
        EventMap.send("load_screen", {"screen": "MainScreen"})


class WeatherInfoScreen(Screen):
    NAME = "WeatherInfoScreen"

    def __init__(self):
        super().__init__()
        self.meta = lv.obj()    # lvgl meta object
        self.lock = Lock()
        self.weatherinfo = None
        
    def load_before(self):
        self.weatherinfo = EventMap.send("get_weather_info", 0)

    def load(self):
        # PrintLog.log(WeatherInfoScreen.NAME, "weatherinfo: {}".format(self.weatherinfo))
        if not self.weatherinfo:
            return
        self.meta.add_style(CommonStyle.default, lv.PART.MAIN | lv.STATE.DEFAULT)


        self.lab_temperature = lv.label(self.meta)
        self.lab_temperature.align(lv.ALIGN.TOP_MID, 0, 40)
        self.temperature = self.weatherinfo[1]
        self.lab_temperature.set_text(self.temperature)

        img = lv.img(self.meta)
        img.align(lv.ALIGN.TOP_MID, 0, 80)
        img.set_size(32, 32)
        img.set_src(self.weatherinfo[0][1])

    def back_press(self, event=None, msg=None):
        EventMap.send("load_screen", {"screen": "WeatherScreen"})

        # with self.lock:
        #     if not self.qr_weather:
        #         return
        #     self.qr_weather.delete()
        #     self.qr_imei = None
            

class DeviceScreen(Screen):
    NAME = "DeviceScreen"

    def __init__(self):
        super().__init__()
        self.meta = lv.obj()    # lvgl meta object

        self.btn_list = []
        self.btn_list_name = ["固件版本", "IMEI", "ICCID"]
        self.curr_idx = 0
        self.count = len(self.btn_list_name)

    def load(self):
        self.meta.add_style(CommonStyle.default, lv.PART.MAIN | lv.STATE.DEFAULT)

        # 列表------------------------------------------------------------------------------------------
        self.list_menu = lv.list(self.meta)
        self.list_menu.set_pos(0, 20)
        self.list_menu.set_size(128, 140)
        self.list_menu.set_style_pad_left(0, 0)
        self.list_menu.set_style_pad_right(0, 0)
        self.list_menu.set_style_pad_top(0, 0)
        self.list_menu.set_style_pad_row(1, 0)
        self.list_menu.add_style(CommonStyle.container_bgffffff, lv.PART.MAIN | lv.STATE.DEFAULT)
        self.list_menu.add_style(MainScreenStyle.list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.DEFAULT)
        self.list_menu.add_style(MainScreenStyle.list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.SCROLLED)
        # 添加管理列表------------------------------------------------------------------------------------------
        self.btn_list = []
        for idx, item in enumerate(self.btn_list_name):
            btn = lv.btn(self.list_menu)
            btn.set_pos(20, 0)
            btn.set_size(128, 34)
            btn.add_style(MainScreenStyle.btn_group, lv.PART.MAIN | lv.STATE.DEFAULT)
            img = lv.img(btn)
            img.align(lv.ALIGN.LEFT_MID, 10, 0)
            img.set_size(32, 32)
            img.set_src('U:/img/number_{}.png'.format(idx + 1))
            lab = lv.label(btn)
            lab.align(lv.ALIGN.LEFT_MID, 50, 10)
            lab.set_size(128, 30)
            lab.set_text(item)
            self.btn_list.append((btn, img, lab))
        self.add_state()

    def add_state(self):    # 添加选中状态
        currBtn = self.list_menu.get_child(self.curr_idx)
        currBtn.set_style_bg_color(lv.color_make(0xe6, 0x94, 0x10), lv.PART.MAIN | lv.STATE.DEFAULT)
        currBtn.set_style_bg_grad_color(lv.color_make(0xe6, 0x94, 0x10), lv.PART.MAIN | lv.STATE.DEFAULT)
        self.btn_list[self.curr_idx][2].set_long_mode(lv.label.LONG.SCROLL_CIRCULAR)
        currBtn.scroll_to_view(lv.ANIM.OFF)

    def clear_state(self):  # 清除选中状态
        currBtn = self.list_menu.get_child(self.curr_idx)
        currBtn.set_style_bg_color(LVGLColor.BASE_COLOR_WHITE, lv.PART.MAIN | lv.STATE.DEFAULT)
        currBtn.set_style_bg_grad_color(LVGLColor.BASE_COLOR_WHITE, lv.PART.MAIN | lv.STATE.DEFAULT)
        self.btn_list[self.curr_idx][2].set_long_mode(lv.label.LONG.SCROLL_CIRCULAR)
        currBtn.scroll_to_view(lv.ANIM.OFF)
    
    def up_press(self):
        """
        作为滚动按键
        """
        self.clear_state()
        self.curr_idx = self.prev_idx(self.curr_idx, self.count)
        self.add_state()

    def down_press(self, event=None, msg=None):
        self.clear_state()
        self.curr_idx = self.next_idx(self.curr_idx, self.count)
        self.add_state()

    def menu_press(self, event=None, msg=None):
        if self.curr_idx ==0:
            EventMap.send("load_screen", {"screen": "FirmwareScreen"})
        elif self.curr_idx == 1:
            EventMap.send("load_screen", {"screen": "IMEIScreen"})
        elif self.curr_idx == 2:
            EventMap.send("load_screen", {"screen": "ICCIDScreen"})
        elif self.curr_idx == 3:
            EventMap.send("load_screen", {"screen": "LbsInfoScreen"})

    def back_press(self, event=None, msg=None):
        EventMap.send("load_screen", {"screen": "MainScreen"})
        if self.curr_idx > 0:
            self.clear_state()
            self.curr_idx = 0


class ICCIDScreen(Screen):
    NAME = "ICCIDScreen"

    def __init__(self):
        super().__init__()
        self.meta = lv.obj()    # lvgl meta object

    def load(self):
        self.meta.add_style(CommonStyle.default, lv.PART.MAIN | lv.STATE.DEFAULT)

        self.lab_title = lv.label(self.meta)
        self.lab_title.align(lv.ALIGN.TOP_MID, 0, 50)
        self.lab_title.set_text("ICCID")
        self.lab_iccid = lv.label(self.meta)
        self.lab_iccid.set_size(98, 80)
        self.lab_iccid.set_long_mode(lv.label.LONG.SCROLL)
        self.lab_iccid.align(lv.ALIGN.TOP_MID, 0, 80)
        self.lab_iccid.set_text(EventMap.send("devinfoservice__get_iccid"))

    def back_press(self, event=None, msg=None):
        EventMap.send("load_screen", {"screen": "DeviceScreen"})
        self.lab_iccid.set_text("")


class IMEIScreen(Screen):
    NAME = "IMEIScreen"

    def __init__(self):
        super().__init__()
        self.meta = lv.obj()    # lvgl meta object
        self.lock = Lock()
        self.qr_imei = None
        self.imei = None

    def load(self):
        self.meta.add_style(CommonStyle.default, lv.PART.MAIN | lv.STATE.DEFAULT)

        # self.lab_title = lv.label(self.meta)
        # self.lab_title.align(lv.ALIGN.TOP_MID, 0, 30)
        # self.lab_title.set_text("IMEI")

        self.lab_imei = lv.label(self.meta)
        self.lab_imei.align(lv.ALIGN.TOP_MID, 0, 20)
        self.imei = EventMap.send("devinfoservice__get_imei")
        self.lab_imei.set_text(self.imei)

        if None == self.imei:
            return
        if None == self.qr_imei:
            self.qr_imei = lv.qrcode(self.meta, 120, LVGLColor.BASE_COLOR_WHITE, LVGLColor.BASE_COLOR_BLACK)
            self.qr_imei.align(lv.ALIGN.TOP_MID, 0, 35)
            self.qr_imei.update(self.imei, len(self.imei))
            self.qr_imei.set_style_border_color(LVGLColor.BASE_COLOR_WHITE, 0)
            self.qr_imei.set_style_border_width(0, 0)

    def back_press(self, event=None, msg=None):
        EventMap.send("load_screen", {"screen": "DeviceScreen"})

        with self.lock:
            if not self.qr_imei: 
                return
            self.qr_imei.delete()
            self.qr_imei = None


class FirmwareScreen(Screen):
    NAME = "FirmwareScreen"

    def __init__(self):
        super().__init__()
        self.meta = lv.obj()    # lvgl meta object

    def load(self):
        self.meta.add_style(CommonStyle.default, lv.PART.MAIN | lv.STATE.DEFAULT)

        self.lab_title = lv.label(self.meta)
        self.lab_title.align(lv.ALIGN.TOP_MID, 0, 50)
        self.lab_title.set_text("Firmware")

        self.lab_fw = lv.label(self.meta)
        self.lab_fw.align(lv.ALIGN.TOP_MID, 5, 80)
        self.lab_fw.set_size(128, 60)
        self.lab_fw.set_text( EventMap.send("devinfoservice__get_firmware") )

    def back_press(self, event=None, msg=None):
        EventMap.send("load_screen", {"screen": "DeviceScreen"})


class PocUI(AbstractLoad):

    def __init__(self):
        self.bar_list = []
        self.msgbox_list = []
        self.screen_list = []
        self.curr_screen = None
        self.lcd = g_lcd

        self.__poc_speak_status = False     # 默认不处于对讲中
        self.__poc_play_status = False      # 默认不处于播放中
        self.lcd_sleep_time = 15  # 息屏时间(s)
        self.lcd_sleep_timer = osTimer()
        
        self.msgbox_close_timer = osTimer()

    def start(self):
        EventMap.bind("load_screen", self.load_screen)      # 加载屏幕
        EventMap.bind("load_msgbox", self.load_msgbox)      # 加载消息框
        EventMap.bind("close_msgbox", self.close_msgbox)    # 关闭消息框
        EventMap.bind("poc_play_status", self.poc_play_status) 
        EventMap.bind("PTT_PRESS", self.ppt_press)
        EventMap.bind("PTT_RELEASE", self.ppt_release)
        EventMap.bind("lcd_state_manage", self.lcd_sleep_enable)
        
        EventMap.bind("UP_PRESS", self.up_press)  
        EventMap.bind("DOWN_PRESS", self.down_press)
        EventMap.bind("MENU_PRESS", self.menu_press)
        EventMap.bind("BACK_PRESS", self.back_press)

        EventMap.bind("OK_PRESS", self.ok_press)
        EventMap.bind("OK_LONG", self.ok_long)
        

        EventMap.bind("PWK_PRESS", self.pwk_press)
        EventMap.bind("PWK_LONG", self.pwk_long)
        EventMap.bind("PWK_RELEASE", self.pwk_release)

        EventMap.bind("ENCODER_LEFT", self.encoder_left)
        EventMap.bind("ENCODER_RIGHT", self.encoder_right)

        for bar in self.bar_list: bar.instance_after()
        for box in self.msgbox_list: box.instance_after()
        for src in self.screen_list: src.instance_after()

        EventMap.send("load_screen", {"screen": WelcomeScreen.NAME})
        EventMap.send("blink_led", (2, 0.5), 1)  # 绿灯慢闪
        PrintLog.log("PocUI", "UI load finished.")
        self.lcd_sleep_enable()
    
    def load_msgbox(self, event, msg):
        """
        加载消息框, 注意msg的格式:
        {
            "type": "promptbox", # 默认提示框
            "title": "[promptbox]"
            "msg": "hello world",
            "mode": 0
        }
        """
        if isinstance(msg, dict):
            _type = msg.get("type", PromptBox.NAME) # 默认提示框
            _type = "{}__show".format(type.lower())
            _msg = {
                "meta": self.curr_screen.meta,
                "msg": msg.get("msg", "[promptbox]"),
                "mode": msg.get("mode", 0)
            }
            EventMap.send(_type, _msg)
        else:
            _msg = {
                "meta": self.curr_screen.meta,
                "title": "[promptbox]",
                "msg": msg,
                "mode": 0
            }
            EventMap.send("promptbox__show", _msg)

    def close_msgbox(self, event, msg):
        """
        在这里对所有消息框发送关闭消息
        """
        EventMap.send("promptbox__close")

    def load_screen(self, event, msg):
        """
        加载UI屏幕
        """
        PrintLog.log("PocUI", "load screen:{}".format(msg["screen"]))
        for scr in self.screen_list:
            if scr.NAME != msg["screen"]:
                continue
            if self.curr_screen:
                if scr.NAME != self.curr_screen.NAME:
                    scr.set_last_screen(self.curr_screen.NAME)
                self.curr_screen.deactivate()
            self.curr_screen = scr
            # PrintLog.log("PocUI", "load screen:{}".format(scr.NAME))

            # 加载屏幕之前先加载屏幕栏
            if self.curr_screen.NAME != "WelcomeScreen":
                EventMap.send("menubar__show", self.curr_screen.meta)

            scr.load_before()
            scr.load()
            scr.load_after()
            lv.img.cache_invalidate_src(None)
            lv.img.cache_set_size(8)
            lv.scr_load(self.curr_screen.meta)  # load lvgl meta object

    def add_bar(self, bar):
        self.bar_list.append(bar)
        return self

    def add_msgbox(self, msgbox):
        self.msgbox_list.append(msgbox)
        return self

    def add_screen(self, screen):
        self.screen_list.append(screen)
        return self

    def poc_play_status(self, event, play_staus):
        """
        poc播放状态
        """
        self.__poc_play_status = play_staus
        self.lcd_sleep_timer.stop()
        g_lcd.display_on()

        # 恢复自动息屏
        if not self.__poc_play_status:
            self.lcd_sleep_enable()

    def lcd_sleep_enable(self, bol=True):
        """
        LCD睡眠使能

        :param bol: 是否允许自动息屏
        """
        self.lcd_sleep_timer.stop()
        if bol:
            self.lcd.display_on()
            PrintLog.log("PocUI", "lcd exit sleep.")
            self.lcd_sleep_timer.start(self.lcd_sleep_time * 1000, 1, lambda arg: self.lcd_sleep_enable(0))   # 10s之后自动息屏
        else:
            if self.__poc_speak_status or self.__poc_play_status:
                PrintLog.log("PocUI", " poc speaking... can't sleep!")
                return
            # self.lcd.display_off()  # 测试阶段暂不息屏
            PrintLog.log("PocUI", "lcd enter sleep.")

    def ppt_press(self, event, msg):
        """
        ptt 长按
        """
        EventMap.send_stop("blink_led") # 停止闪烁LED
        EventMap.send("switch_led", 1) # red常亮
        self.lcd_sleep_enable()  # 不允许黑屏
        if not EventMap.send("pocservice__get_rocker_arm") and EventMap.send("pocservice__get_login_status"):
            EventMap.send("mediaservice__tts_play", ("您已被关闭发言", 1))
            return
        EventMap.send("pocservice__call_member_status", 1)
        self.__poc_speak_status = EventMap.send("pocservice__speaker_enable", 1)  # 开启对讲
        

    def ppt_release(self, event, msg):
        """
        ptt 抬起
        """
        EventMap.send("blink_led", (2, 0.5), 1)  # 绿灯慢闪
        if not self.__poc_speak_status:
            return
        self.__poc_speak_status = 0
        EventMap.send("pocservice__speaker_enable", 0)
        EventMap.send("pocservice__call_member_status", 0)

    def up_press(self, event, msg):
        self.lcd_sleep_enable()
        self.curr_screen.up_press()

    def down_press(self, event, msg):
        self.lcd_sleep_enable()
        self.curr_screen.down_press()

    def menu_press(self, event, msg):
        self.lcd_sleep_enable()
        self.curr_screen.menu_press()

    def back_press(self, event, msg):
        self.lcd_sleep_enable()
        self.curr_screen.back_press()
        
    def ok_press(self, event, msg):
        self.lcd_sleep_enable()
        pass
    
    def ok_long(self, event, msg):
        self.lcd_sleep_enable()
        pass
        # 单呼


    def pwk_press(self, event, msg):
        EventMap.send("load_msgbox", "关机中...")
        
    def pwk_long(self, event, msg):
        from misc import Power
        Power.powerDown()
    
    def pwk_release(self, event, msg):
        EventMap.send("close_msgbox")
    
    
    def encoder_left(self, event, msg):
        EventMap.send("mediaservice__vol_add", None)
        EventMap.send("load_msgbox", 'add vol')
        self.msgbox_close_timer.start(2 * 1000, 0, lambda arg: EventMap.send("close_msgbox"))
    
    def encoder_right(self, event, msg):
        EventMap.send("mediaservice__vol_reduce", None)
        EventMap.send("load_msgbox", 'reduce vol')
        self.msgbox_close_timer.start(2 * 1000, 0, lambda arg: EventMap.send("close_msgbox"))
