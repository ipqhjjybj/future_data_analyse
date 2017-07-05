

import matplotlib.pyplot as plt  
import matplotlib
import datetime
import pylab
import tushare as ts


# plotdat = ts.get_k_data('600000' , start='2015-01-01', end = '2015-01-30')
plotdat = ts.get_k_data('600000' )
dates = list(plotdat["date"])
dates = [datetime.datetime.strptime(x , "%Y-%m-%d") for x in dates]


#datetime.datetime.strptime("20130810", "%Y%m%d")  
fig = plt.figure()

ax1 = plt.subplot2grid((4,4),(0,0),rowspan=3, colspan=4)

matplotlib.finance.candlestick_ohlc(ax1,
		list(
			zip(list(matplotlib.dates.date2num(dates)),
			plotdat["open"].tolist(),plotdat["high"].tolist(),
			plotdat["low"].tolist(),plotdat["close"].tolist())
			),colorup = "#77d879",colordown='#db3f3f')

ax2 = plt.subplot2grid((4,4),(3,0),rowspan=1,colspan=4)
ax2.bar( matplotlib.dates.date2num(dates) , plotdat["volume"] / 10000.0 , width=0.4 , align='center')
plt.grid = True

ax1.xaxis.set_major_locator(matplotlib.dates.MonthLocator())
ax1.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%Y-%m-%d"))
ax2.xaxis.set_major_locator(matplotlib.dates.MonthLocator())
ax2.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%Y-%m-%d"))
for label in ax2.xaxis.get_ticklabels():
	label.set_rotation(60)
ax1.set_title("60000.SH")
ax1.set_ylabel("Price")
ax2.set_ylabel("Volume(ten thousand)")


plt.setp(ax1.get_xticklabels() , visible = False)
plt.setp(ax1.yaxis.get_ticklabels()[0] , visible = False)
plt.subplots_adjust(bottom=0.2,top=0.9,hspace=0)
# quotes = list(zip(list(date2num(plotdat.index.tolist())),plotdat["open"].tolist(),plotdat["high"].tolist(),plotdat["low"].tolist(),plotdat["close"].tolist()))
# print quotes
# candlestick_ohlc(ax,quotes, colorup = "black",colordown='red')

plt.show()