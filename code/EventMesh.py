import _thread
import usys


class EventStore(object):
    def __init__(self):
        self.map = dict()
        self.log = None
        self.__filters = []

    def add_filter(self, flt):
        self.__filters.append(flt)

    def append(self, event, cb):
        self.map[event] = cb

    def fire_async(self, event, msg):
        if event in self.map:
            _thread.start_new_thread(self.map[event], (event, msg))
            if self.log:
                self.log.info("ASYNC executed (event) -> {} (params) -> {} (result) -> {}".format(event, msg, None))

    def fire_sync(self, event, msg):
        res = None
        try:
            if event in self.map:
                res = self.map[event](event, msg)
        except Exception as e:
            usys.print_exception(e)
        if event not in self.__filters:
            if self.log:
                self.log.info("SYNC executed (event) -> {} (params) -> {} (result) -> {}".format(event, msg, res))
        return res


event_store = EventStore()


def subscribe(event, cb):
    """
    subscribe event and cb
    """
    return event_store.append(event, cb)


def publish(event, msg=None):
    """
    publish event and msg
    """
    return publish_sync(event, msg)


def publish_async(event, msg=None):
    """
    异步发送
    """
    return event_store.fire_async(event, msg)


def publish_sync(event, msg=None):
    """
    同步发送
    """
    return event_store.fire_sync(event, msg)


def set_log(log_adapter):
    event_store.log = log_adapter


def add_filter(flt):
    event_store.add_filter(flt)
