# -*- coding:utf-8 -*-

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime

from matplotlib.dates import DateFormatter, WeekdayLocator, DayLocator, MONDAY
from matplotlib.finance import quotes_historical_yahoo,quotes_historical_yahoo_ohlc, candlestick_ohlc
from pylab import figure, show 
from matplotlib.dates import YearLocator, MonthLocator, DateFormatter

#从雅虎财经获取历史行情
date1 = datetime.date(2017, 1, 1)
date2 = datetime.date(2017, 4, 30)
quotes = quotes_historical_yahoo('MSFT', date1, date2) 
if len(quotes) == 0:
    raise SystemExit

#创建一个子图
fig, ax = plt.subplots()
fig.subplots_adjust(bottom=0.2)

#设置主要刻度和显示格式
mondays = WeekdayLocator(MONDAY)
mondaysFormatter = DateFormatter('%Y-%m-%d')
ax.xaxis.set_major_locator(mondays)
ax.xaxis.set_major_formatter(mondaysFormatter)

#设置次要刻度和显示格式
alldays = DayLocator()
alldaysFormatter = DateFormatter('%d')
ax.xaxis.set_minor_locator(alldays)
#ax.xaxis.set_minor_formatter(alldaysFormatter)


#设置x轴为日期
ax.xaxis_date()
ax.autoscale_view()
#X轴刻度文字倾斜45度
plt.setp(plt.gca().get_xticklabels(), rotation=45, horizontalalignment='right')

candlestick_ohlc(ax, quotes, width=0.6, colorup='r', colordown='g')
ax.grid(True)
plt.title('MSFT')
plt.show()