import signal
from contextlib import contextmanager

class TimeoutException(Exception): pass

@contextmanager
def time_limit(seconds):
    def signal_handler(signum, frame):
        raise TimeoutException, "Timed out!"
    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)
        print 1

def some_method():
    sleep(100000)
try:
    with time_limit(5):
        response = some_method()
except TimeoutException:
    print "log_something()"

print "do_the_rest()"
