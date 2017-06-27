import time
import thread
class TimeLimitExpired(Exception): pass

def timelimit(timeout, func, args=(), kwargs={}):
    """ Run func with the given timeout. If func didn't finish running
        within the timeout, raise TimeLimitExpired
    """
    import threading
    class FuncThread(threading.Thread):
        def __init__(self):
            threading.Thread.__init__(self)
            self.result = None

        def run(self):
            self.result = func(*args, **kwargs)

        def _stop(self):
            if self.isAlive():
                try:
                    threading.Thread._Thread__stop(self)
                except Exception,ex:
                    print ex
    
    it = FuncThread()
    try:
        it.start()
        it.join(timeout)
        if it.isAlive():
            it._stop()
            raise TimeLimitExpired()
        else:
            return it.result
    except Exception,ex:
        print "##"
        print ex

def fn():
    while True:
        a = 1

try:
    for i in range(1):
        timelimit(3, fn)
except Exception,ex:
    print ex

if __name__ == '__main__':  

    import os
    os.system('taskkill /f /im "Excel.exe"')
