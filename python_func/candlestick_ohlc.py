

import matplotlib.pyplot as plt  
import matplotlib
import datetime
import pylab
import tushare as ts


plotdat = ts.get_k_data('600000')
dates = list(plotdat["date"])
dates = [datetime.datetime.strptime(x , "%Y-%m-%d") for x in dates]

#datetime.datetime.strptime("20130810", "%Y%m%d")  
fig = plt.figure(1, figsize=(12,6))
ax  = fig.add_subplot(111)

#print plotdat["open"].tolist()
print ax
#matplotlib.finance.candlestick2_ohlc(ax, plotdat["open"].tolist(),plotdat["high"].tolist(),plotdat["low"].tolist(),plotdat["close"].tolist(), width=4, colorup='r', colordown='g', alpha=0.75)


matplotlib.finance.candlestick_ohlc(ax,
		list(
			zip(list(matplotlib.dates.date2num(dates)),
			plotdat["open"].tolist(),plotdat["high"].tolist(),
			plotdat["low"].tolist(),plotdat["close"].tolist())
			),colorup = "black",colordown='red')

plt.setp(ax.get_xticklabels() , visible = False)
plt.setp(ax.yaxis.get_ticklabels()[0] , visible = False)
plt.subplots_adjust(bottom=0.2,top=0.9,hspace=0)
# quotes = list(zip(list(date2num(plotdat.index.tolist())),plotdat["open"].tolist(),plotdat["high"].tolist(),plotdat["low"].tolist(),plotdat["close"].tolist()))
# print quotes
# candlestick_ohlc(ax,quotes, colorup = "black",colordown='red')

plt.show()