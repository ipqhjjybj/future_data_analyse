y1=y[79:91]
y2=y[91:102]
x1=range(0,len(y1))
x2=range(0,len(y2))
plt.figure(figsize=(10, 6))
plt.plot(x1,y1,'',label="2015年")
plt.plot(x2,y2,'',label="2016年")
plt.title('2015-2016年月XX事件数')
plt.legend(loc='upper right')
plt.xticks((0,2,4,6,8,10),('1月','3月','5月','7月','9月','11月'))
plt.xlabel('月份')
plt.ylabel('XX事件数')
plt.grid(x1)
plt.show()