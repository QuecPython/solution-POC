
import sys

try:
    from common import AbstractLoad, PrintLog
    from dev.key import KeyManger
    from services import *
    from ui.ui import PocUI,\
                      MenuBar,\
                      MainScreen,\
                      WelcomeScreen,\
                      PromptBox,\
                      MemberScreen,\
                      GroupScreen,\
                      SettingScreen,\
                      DeviceScreen,\
                      ICCIDScreen,\
                      IMEIScreen,\
                      FirmwareScreen
except:
    from usr.common import AbstractLoad, PrintLog
    from usr.dev.key import KeyManger
    from usr.services import *
    from usr.ui.ui import PocUI,\
                          MenuBar,\
                          MainScreen,\
                          WelcomeScreen,\
                          PromptBox,\
                          MemberScreen,\
                          GroupScreen,\
                          SettingScreen,\
                          DeviceScreen,\
                          ICCIDScreen,\
                          IMEIScreen,\
                          FirmwareScreen



class App(object):
    __service_list = []
    __ui = None
    __key = None

    @classmethod
    def set_ui(cls, ui):
        cls.__ui = ui

    @classmethod
    def add_key(cls, key):
        cls.__key = key

    @classmethod
    def add_bar(cls, bar:AbstractLoad):
        """
        这里只负责向UI添加屏幕栏, 屏幕栏由UI进行管理
        """
        try:
            if isinstance(bar, AbstractLoad):
                cls.__ui.add_bar(bar)     
        except Exception as e:
            raise Exception("[App](abort) add_bar error: ", e)
        return cls

    @classmethod
    def add_msgbox(cls, msgbox:AbstractLoad):
        """
        这里只负责向UI添加消息框, 消息框由UI进行管理
        """
        try:
            if isinstance(msgbox, AbstractLoad):
                cls.__ui.add_msgbox(msgbox)     
        except Exception as e:
            raise Exception("[App](abort) add_msgbox error: ", e)
        return cls

    @classmethod
    def add_screen(cls, screen:AbstractLoad):
        """
        这里只负责向UI添加屏幕, 屏幕由UI进行管理
        """
        if None == cls.__ui:
            raise Exception("UI is None.")
        try:
            if isinstance(screen, AbstractLoad):
                cls.__ui.add_screen(screen)    
        except Exception as e:
            raise Exception("[App](abort) add_screen error: ", e)
        return cls
        
    @classmethod
    def add_service(cls, service:AbstractLoad):
        """
        添加服务
        """
        try:
            if isinstance(service, AbstractLoad):
                service.instance_after()   # 初始化服务
                cls.__service_list.append(service)
        except Exception as e:
            raise Exception("[App](abort) add_service error: ", e)
        return cls

    @classmethod
    def exec(cls):
        """
        启动App
        """
        if None == cls.__ui:
            raise Exception("[App](abort) exec interrupt, UI is null.")
        try:
            # start ui
            cls.__ui.start()
            
            import lvgl as lv
            lv.task_handler()
            
            # start services
            for service in App.__service_list:
                service.load_before()
                service.load()
                service.load_after()
        except Exception as e:
            print("[App] exec error: ", e)



if __name__ == '__main__':
    
    #=== 1.添加按键 ===
    App.add_key(KeyManger())

    #=== 2.添加主UI ===
    App.set_ui(PocUI())

    #=== 3.添加屏幕栏 ===
    App.add_bar(MenuBar())

    #=== 4.添加消息框 ===
    App.add_msgbox(PromptBox())

    #=== 5.添加UI屏幕 ===
    App.add_screen( MenuBar()) \
        .add_screen( MainScreen()) \
        .add_screen( WelcomeScreen() ) \
        .add_screen( PromptBox() ) \
        .add_screen( MemberScreen() ) \
        .add_screen( GroupScreen() ) \
        .add_screen( SettingScreen() ) \
        .add_screen( DeviceScreen() ) \
        .add_screen( ICCIDScreen() ) \
        .add_screen( IMEIScreen()) \
        .add_screen( FirmwareScreen() )
    
    #=== 6.添加服务 ===
    App.add_service( NetService()) \
        .add_service( PocService()) \
        .add_service( MediaService()) \
        .add_service( DevInfoService() ) 

    #=== 7.运行App ===
    App.exec()



                      