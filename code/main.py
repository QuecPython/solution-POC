from usr.common import Abstract
from machine import LCD, Pin


class App(object):
    def __init__(self):
        self.managers = []

    def append_manager(self, manager):
        if isinstance(manager, Abstract):
            manager.post_processor_after_instantiation()
            self.managers.append(manager)
        return self

    def start(self):
        for manager in self.managers:
            manager.post_processor_before_initialization()
            manager.initialization()
            manager.post_processor_after_initialization()


class PocApp(App):
    def __init__(self):
        super(PocApp, self).__init__()
        self.__ui = None

    def set_ui(self, ui):
        self.__ui = ui

    def start(self):
        if self.__ui is not None:
            self.__ui.start()
        super().start()
        self.__ui.finish()


white = 0xFFFF  # 白色
black = 0x0000
XSTART_H = 0xf0  # Start point X coordinate high byte register
XSTART_L = 0xf1  # Start point X coordinate low byte register
XEND_H = 0xE0  # End point X coordinate high byte register
XEND_L = 0xE1  # End point X coordinate low byte register
YSTART_H = 0xf2  # Start point y coordinate high byte register
YSTART_L = 0xf3  # Start point y coordinate low byte register
YEND_H = 0xE2  # End point y coordinate high byte register
YEND_L = 0xE3  # End point y coordinate low byte register

XSTART = 0xD0  # Start point X coordinate register (2byte)
XEND = 0xD1  # End point X coordinate register (2byte)
YSTART = 0xD2  # Start point Y coordinate register (2byte)
YEND = 0xD3  # End point Y coordinate register (2byte)


class CustomError(Exception):
    def __init__(self, ErrorInfo):
        super().__init__(self)
        self.errorinfo = ErrorInfo

    def __str__(self):
        return self.errorinfo


class Peripheral_LCD(object):
    '''
    LCD通用类,定义LCD屏的通用行为
    开放接口：
    DrawPoint(x, y, color),DrawLine(x0, y0, x1, y1, color),DrawRectangle(x0, y0, x1, y1, color)
    Clear(color),DrawCircle(x0, y0, r, color),ShowChar(x, y, xsize, ysize, ch_buf, fc, bc)
    ShowAscii(x, y, xsize, ysize, ch, fc, bc),ShowAsciiStr(x, y, xsize, ysize, str_ascii, fc, bc)
    ShowJpg(name, start_x, start_y), lcd_show_chinese(x, y, xsize, ysize, ch, fc, bc),
    lcd_show_chinese_str(x, y, xsize, ysize, str_ch, fc, bc),lcd_show_image(image_data, x, y, width, heigth)
    lcd_show_image_file(path, x, y, width, heigth, h)
    '''

    def __init__(self, child_self=None):

        if child_self is None:
            raise CustomError("child LCD should be init first. ")
        else:
            self._child_self = child_self

    def DrawPoint(self, x, y, color):
        '''
        画点
        :param x: x
        :param y: y
        :param color: color
        '''
        tmp = color.to_bytes(2, 'little')
        self._child_self.lcd.lcd_write(bytearray(tmp), x, y, x, y)

    def Clear(self, color):
        '''
        清屏
        :param color: color
        '''
        self._child_self.lcd.lcd_clear(color)

    def Fill(self, x_s, y_s, x_e, y_e, color):
        '''
        填充以起始坐标和结束坐标为对角线的矩形
        :param x_s: 起始x坐标
        :param y_s: 起始y坐标
        :param x_e: 结束x坐标
        :param y_e: 结束y坐标
        :param color: color
        '''
        tmp = color.to_bytes(2, 'little')
        count = (x_e - x_s + 1) * (y_e - y_s + 1)

        color_buf = bytearray(0)

        for i in range(count):
            color_buf += tmp

        self._child_self.lcd.lcd_write(color_buf, x_s, y_s, x_e, y_e)


class LCD_ST7735(Peripheral_LCD):
    def __init__(self, InitData=None, width=128, height=128, clk=26000, dir=0):
        self.gpio = None
        self.lcd = None
        self._lcd_w = None
        self._lcd_h = None
        self._LcdInit(InitData, width, height, dir, clk)
        super().__init__(self)

    def _LcdInit(self, InitData, width, height, dir, clk):
        self.gpio = Pin(Pin.GPIO14, Pin.OUT, Pin.PULL_DISABLE, 1)
        L2R_U2D = 0
        L2R_D2U = 1
        R2L_U2D = 2
        R2L_D2U = 3

        U2D_L2R = 4
        U2D_R2L = 5
        D2U_L2R = 6
        D2U_R2L = 7

        regval = 0
        if (dir == L2R_U2D):
            regval |= (0 << 7) | (0 << 6) | (0 << 5)
        elif dir == L2R_D2U:
            regval |= (1 << 7) | (0 << 6) | (0 << 5)
        elif dir == R2L_U2D:
            regval |= (0 << 7) | (1 << 6) | (0 << 5)
        elif dir == R2L_D2U:
            regval |= (1 << 7) | (1 << 6) | (0 << 5)
        elif dir == U2D_L2R:
            regval |= (0 << 7) | (0 << 6) | (1 << 5)
        elif dir == U2D_R2L:
            regval |= (0 << 7) | (1 << 6) | (1 << 5)
        elif dir == D2U_L2R:
            regval |= (1 << 7) | (0 << 6) | (1 << 5)
        elif dir == D2U_R2L:
            regval |= (1 << 7) | (1 << 6) | (1 << 5)
        else:
            regval |= (0 << 7) | (0 << 6) | (0 << 5)

        self._lcd_w = width
        self._lcd_h = height

        if (regval & 0X20):
            if (width < height):
                self._lcd_w = height
                self._lcd_h = width
        else:
            if (width > height):
                self._lcd_w = height
                self._lcd_h = width

        init_data = (
            0, 0, 0x11,
            2, 0, 120,

            0, 3, 0xb1,
            1, 1, 0x01,
            1, 1, 0x08,
            1, 1, 0x05,

            0, 3, 0xb2,
            1, 1, 0x05,
            1, 1, 0x3c,
            1, 1, 0x3c,

            0, 6, 0xb3,
            1, 1, 0x05,
            1, 1, 0x3c,
            1, 1, 0x3c,
            1, 1, 0x05,
            1, 1, 0x3c,
            1, 1, 0x3c,

            0, 1, 0xb4,
            1, 1, 0x03,

            0, 3, 0xc0,
            1, 1, 0x28,
            1, 1, 0x08,
            1, 1, 0x04,

            0, 1, 0xc1,
            1, 1, 0xc0,

            0, 2, 0xc2,
            1, 1, 0x0d,
            1, 1, 0x00,

            0, 2, 0xc3,
            1, 1, 0x8d,
            1, 1, 0x2a,

            0, 2, 0xc4,
            1, 1, 0x8d,
            1, 1, 0xee,

            0, 1, 0xc5,
            1, 1, 0x12,

            0, 1, 0x36,
            1, 1, 0x68,

            0, 16, 0xe0,
            1, 1, 0x04,
            1, 1, 0x22,
            1, 1, 0x07,
            1, 1, 0x0a,
            1, 1, 0x2e,
            1, 1, 0x30,
            1, 1, 0x25,
            1, 1, 0x2a,
            1, 1, 0x28,
            1, 1, 0x26,
            1, 1, 0x2e,
            1, 1, 0x3a,
            1, 1, 0x00,
            1, 1, 0x01,
            1, 1, 0x03,
            1, 1, 0x13,

            0, 16, 0xe1,
            1, 1, 0x04,
            1, 1, 0x16,
            1, 1, 0x06,
            1, 1, 0x0d,
            1, 1, 0x2d,
            1, 1, 0x26,
            1, 1, 0x23,
            1, 1, 0x27,
            1, 1, 0x27,
            1, 1, 0x25,
            1, 1, 0x2d,
            1, 1, 0x3b,
            1, 1, 0x00,
            1, 1, 0x01,
            1, 1, 0x04,
            1, 1, 0x13,

            0, 1, 0x3a,
            1, 1, 0x05,

            0, 1, 0x35,
            1, 1, 0x00,

            0, 0, 0x29,
            1, 0, 0x2c,
        )
        lcd_set_display_area = (
            0, 4, 0x2a,
            1, 1, XSTART_H,
            1, 1, XSTART_L,
            1, 1, XEND_H,
            1, 1, XEND_L,
            0, 4, 0x2b,
            1, 1, YSTART_H,
            1, 1, YSTART_L,
            1, 1, YEND_H,
            1, 1, YEND_L,
            0, 0, 0x2c,
        )
        lcd_display_on = (
            0, 0, 0x11,
            2, 0, 20,
            0, 0, 0x29,
        )
        lcd_display_off = (
            0, 0, 0x28,
            2, 0, 120,
            0, 0, 0x10,
        )
        if InitData is None:
            self._initData = bytearray(init_data)
        else:
            self._initData = InitData

        self._invalidData = bytearray(lcd_set_display_area)
        self._displayOn = bytearray(lcd_display_on)
        self._displayOff = bytearray(lcd_display_off)

        self.lcd = LCD()
        self.lcd.lcd_init(
            self._initData,
            self._lcd_w,
            self._lcd_h,
            clk,
            1,
            4,
            0,
            self._invalidData,
            self._displayOn,
            self._displayOff,
            None)


if __name__ == '__main__':
    """##############################################主体业务######################################################
    1. 设置网关日志开启功能 -> 调试和日志概览
    2. ui:
        组成对象:
            LCD屏幕 -> LCD_ST7789
            按键事件 -> BtnDevice
    3. ui添加页面:
        add_screen
    4. PocApp 对象
        1. 设置UI -> set_ui
        2. 添加业务需要的管理器(即服务) -> append_manager
    5. 启动PocApp
        start()        
    ##############################################主体业务######################################################"""
    import lvgl as lv

    # 初始化lvgl
    lv.init()
    lcd = LCD_ST7735()
    # Register SDL display driver.
    disp_buf1 = lv.disp_draw_buf_t()
    buf1_1 = bytearray(128 * 128 * 2)
    disp_buf1.init(buf1_1, None, len(buf1_1))
    disp_drv = lv.disp_drv_t()
    disp_drv.init()
    disp_drv.draw_buf = disp_buf1
    disp_drv.flush_cb = lcd.lcd.lcd_write
    disp_drv.hor_res = 128
    disp_drv.ver_res = 128
    disp_drv.register()

    lv.tick_inc(5)
    lv.task_handler()
    print("lvgl init complete end")

    from usr.ui import Poc_Ui, \
        WelcomeScreen, \
        MainScreen, \
        MenuScreen, \
        GroupScreen, \
        MemberScreen, \
        SettingScreen, \
        LbsInfoScreen, \
        WeatherInfoScreen, \
        AboutScreen, \
        NotifyScreen, \
        StdWriteNumber, \
        SettingSleepScreen, \
        SettingCallTimeScreen, \
        SettingBatteryScreen, \
        SettingSimScreen, \
        SettingPlatformScreen, \
        SettingKeypadToneScreen, \
        SettingPttHintToneScreen, \
        KeyLockBox, \
        VolMsgBox, \
        PopupMsgBox, \
        QrCodeMsgBox

    from usr.mgr import ConfigStoreManager, \
        DeviceInfoManager, \
        MediaManager, \
        NetManager, \
        BatteryManager, \
        LowPowerManager, \
        PocManager, \
        LedManage

    import atcmd
    from usr.btn_device_600m import BtnDevice

    bd = BtnDevice()
    bd.start()
    try:
        resp = bytearray(50)
        atcmd.sendSync('AT+MEDCR=0,88,3\r\n', resp, '', 20)
        print(resp)
    except Exception as e:
        print("resp e {}".format(e))
    # UI loader
    app = PocApp()
    poc_ui = Poc_Ui(lcd)
    poc_ui.add_screen(WelcomeScreen()) \
        .add_screen(MainScreen()) \
        .add_screen(MenuScreen()) \
        .add_screen(GroupScreen()) \
        .add_screen(MemberScreen()) \
        .add_screen(SettingScreen()) \
        .add_screen(LbsInfoScreen()) \
        .add_screen(WeatherInfoScreen()) \
        .add_screen(AboutScreen()) \
        .add_screen(NotifyScreen()) \
        .add_screen(StdWriteNumber()) \
        .add_screen(SettingSleepScreen()) \
        .add_screen(SettingCallTimeScreen()) \
        .add_screen(SettingBatteryScreen()) \
        .add_screen(SettingSimScreen()) \
        .add_screen(SettingPlatformScreen()) \
        .add_screen(SettingKeypadToneScreen()) \
        .add_screen(SettingPttHintToneScreen())
    poc_ui.add_msg_box(VolMsgBox()) \
        .add_msg_box(PopupMsgBox()) \
        .add_msg_box(QrCodeMsgBox()) \
        .add_msg_box(KeyLockBox())
    app.append_manager(ConfigStoreManager()) \
        .append_manager(DeviceInfoManager()) \
        .append_manager(MediaManager()) \
        .append_manager(NetManager()) \
        .append_manager(BatteryManager()) \
        .append_manager(LowPowerManager()) \
        .append_manager(PocManager()) \
        .append_manager(LedManage())

    app.set_ui(poc_ui)
    app.start()
