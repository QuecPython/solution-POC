import utime
import _thread
from machine import Pin

try:
    from common import EventMap
except:
    from usr.common import EventMap
    
    


class LedManager(object):
    def __init__(self):
        self.R_light = Pin(Pin.GPIO6, Pin.OUT, Pin.PULL_PU, 0)
        self.G_light = Pin(Pin.GPIO7, Pin.OUT, Pin.PULL_PU, 0)
        self.RGB_RED = 0x01
        self.RGB_GREEN = 0x02
        
    def instance_after(self):
        """订阅此类所有的事件到 EventMesh中"""
        EventMap.bind("switch_led", self.switch)
        EventMap.bind("blink_led", self.blink)

    # msg=1 red灯 msg=2 绿灯  0 关闭
    def switch(self, event, msg):
        self.R_light.write(1) if msg & self.RGB_RED else self.R_light.write(0)
        self.G_light.write(1) if msg & self.RGB_GREEN else self.G_light.write(0)
    
    # msg=(灯索引,休眠时间) 指定某个灯闪烁
    def blink(self, event, msg):
        """Blink the specified color for a given duration."""
        self.switch(None, 0)  # 先关闭所有灯
        while True:
            self.thread_id = _thread.get_ident()
            blink_light = list()
            blink_light.append(self.R_light) if msg[0] & self.RGB_RED else None
            blink_light.append(self.G_light) if msg[0] & self.RGB_GREEN else None

            for i in blink_light:
                i.write(1)
            utime.sleep(msg[1])
            for i in blink_light:
                i.write(0)
            utime.sleep(msg[1])
    
    
    
    
if __name__ == "__main__":
    led = LedManager()
    led.instance_after()