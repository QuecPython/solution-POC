import _thread
import utime
from event_message import Event, EventManager


class Lock(object):

    def __init__(self):
        self.lock = _thread.allocate_lock()

    def __enter__(self, *args, **kwargs):
        self.lock.acquire()

    def __exit__(self, *args, **kwargs):
        self.lock.release()


class LOG_LV(object):
    """日志等级"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Abstract(object):
    def post_processor_after_instantiation(self, *args, **kwargs):
        """实例化后调用"""
        pass

    def post_processor_before_initialization(self, *args, **kwargs):
        """初始化之前调用"""
        pass

    def initialization(self, *args, **kwargs):
        """初始化load"""
        pass

    def post_processor_after_initialization(self, *args, **kwargs):
        """初始化之后调用"""
        pass


class AbstractOutput(object):
    def open(self):
        pass

    def output(self, message, **kwargs):
        pass

    def close(self):
        pass


class PrintLogOutput(AbstractOutput):
    def output(self, message, **kwargs):
        fmt = "{} [ {} ] {} {}"
        print(fmt.format(*message))


class LogService(Abstract):
    """
        default log is async queue
        you can set
    """
    INSTANCE = None
    REPORTER = PrintLogOutput()
    LEVEL = LOG_LV.DEBUG
    MODE = 1
    LEVEL_MAP = {
        LOG_LV.DEBUG: 0,
        LOG_LV.INFO: 1,
        LOG_LV.WARNING: 2,
        LOG_LV.ERROR: 3,
        LOG_LV.CRITICAL: 4
    }

    def __init__(self):
        self.__event = Event(__name__)
        self.__em = EventManager()
        self.__em.register_event(self.__event)

    @classmethod
    def create(cls):
        if not cls.INSTANCE:
            cls.INSTANCE = LogService()
            cls.INSTANCE.start()
        return cls.INSTANCE

    def log_send(self, tag, level, msg, mode):
        if self.MODE:
            mode = self.MODE
        if self.LEVEL_MAP[level] >= self.LEVEL_MAP.get(self.LEVEL, 0):
            output_format = "{ascdate} {asctime}"
            rt = utime.localtime()
            d_f = "{0:02}"
            send_msg = (output_format.format(
                ascdate=str(rt[0]) + "-" + d_f.format(rt[1]) + "-" + d_f.format(rt[2])
                , asctime=d_f.format(rt[3]) + ":" + d_f.format(rt[4]) + ":" + d_f.format(rt[5])
            ), tag, level, msg)
            # self.REPORTER.output(send_msg)
            print("{} [ {} ] {} {}".format(*send_msg))
            # self.__event.post(send_msg)

    def output(self, *args, **kwargs):
        emo = kwargs.get("event_message")
        self.REPORTER.output(emo.msg)

    def start(self):
        self.__event.add_handler(self.output)
        self.__em.start()


class LogAdapter(object):
    """
        log adapter mode
        mode used : adapter proxy single LogService
    """

    def __init__(self, tag, enable=1):
        self.log_service = LogService.create()
        self.tag = tag
        self.enable = enable
        self.mode = 1

    def critical(self, msg):
        if self.enable:
            self.log_service.log_send(self.tag, LOG_LV.CRITICAL, msg, self.mode)

    def debug(self, msg):
        if self.enable:
            self.log_service.log_send(self.tag, LOG_LV.DEBUG, msg, self.mode)

    def info(self, msg):
        if self.enable:
            self.log_service.log_send(self.tag, LOG_LV.INFO, msg, self.mode)

    def warning(self, msg):
        if self.enable:
            self.log_service.log_send(self.tag, LOG_LV.WARNING, msg, self.mode)

    def error(self, msg):
        if self.enable:
            self.log_service.log_send(self.tag, LOG_LV.ERROR, msg, self.mode)
