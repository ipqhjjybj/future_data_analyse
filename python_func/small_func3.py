
import os, sys
import datetime
import time
import logging
try:
  import ipaddress
except ImportError:
  # Python 3.2-
  ipaddress = None
import contextlib
import signal
import hashlib
import base64


@contextlib.contextmanager
def execution_timeout(timeout):
    def timed_out(signum, sigframe):
        raise TimeoutError
    delay, interval = signal.setitimer(signal.ITIMER_REAL, timeout, 0)
    old_hdl = signal.signal(signal.SIGALRM, timed_out)
    now = time.time()
    try:
        yield
    finally:
        # inner timeout must be smaller, or the timer event will be delayed
        if delay:
          elapsed = time.time() - now
          delay = max(delay - elapsed, 0.000001)
        else:
          delay = 0
        signal.setitimer(signal.ITIMER_REAL, delay, interval)
        signal.signal(signal.SIGALRM, old_hdl)
def fn():
    while True:
        a = 1
try:
    with execution_timeout(50):
        fn()
except Exception,ex:
    print "3"
    print ex