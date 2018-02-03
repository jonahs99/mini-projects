from threading import Event, Thread

def call_repeatedly(interval, func, *args):
    stopped = Event()
    def loop():
        while not stopped.wait(interval): # the first call is in `interval` secs
            func(*args)
    Thread(target=loop).start()    
    return stopped.set

def call_once(func, *args):
    def loop():
        func(*args)
    Thread(target=loop).start()