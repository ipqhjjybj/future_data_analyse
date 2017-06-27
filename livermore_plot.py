# encoding: UTF-8

"""
绘制livermore的图
"""

from MongodbClient import *
import matplotlib.pyplot as plt

ShangShenQuShi = "上升趋势".decode('utf-8')
ZiRanHuiShen   = "自然回升".decode('utf-8')
CiJiHuiShen    = "次级回升".decode('utf-8')

XiaJiangQushi  = "下降趋势".decode('utf-8')
ZiRanHuiChe    = "自然回撤".decode('utf-8')
CiJiHuiChe     = "次级回撤".decode('utf-8')

HeiMoShui      = "k"
HongMoShui     = "r"
QianBi         = "b"

RED_LINE       = "r"           # 上升趋势以及自然回调后的线
BLACK_LINE     = "b"           # 下降趋势以及自然回升形成的线

TimeWindow     =  4 		   # 保留最近4个关键点
#b---blue   c---cyan  g---green    k----black
#m---magenta r---red  w---white    y----yellow
#plt.plot(y, 'cx--', y+1, 'mo:', y+2, 'kp-.');  
color_line_dic = {"上升趋势":"kp" , "下降趋势":"rp"}  # 上升趋势黑墨水 k--black，下降趋势红墨水
'''
'-'	    实线	':'	虚线
'--'	破折线	'None',' ',''	什么都不画
'-.'	点划线
'''
#plot(X, S, color="r", lw=4.0, linestyle="-") 
key_horizontal_line = {"上升趋势":"r"}  # 趋势终结时，也就是关键点 所需要画的重要线


key_point_arr     = [] 						# 存储最重要的几个关键点，  (点位,时间, 线的颜色)的格式
Kline_point_arr   = []						# [(datetime,Y,"上升趋势",'r')] 存储剩下的趋势点, 上升趋势黑墨水 k--black，下降趋势红墨水 ， 其他栏的点，铅笔

def main(param1 = 6  , param2 = 3):
	data = MongoClient.getBetweenClose("VnTrader_1Min_Db","hc1710",'2017-06-01','2017-08-24')
	big_condition = ShangShenQuShi
	point_color   = "k"
	if data[1][1] < data[0][1]:
		big_condition = XiaJiangQushi 
		point_color   = "r"
	Kline_point_arr.append( (data[0][0] ,  data[0][1], big_condition , 'r'))
	for i in range(1,len(data)):
		(x, y) = data[i]
		if big_condition   == ShangShenQuShi:
			if  y > Kline_point_arr[-1][1]:
				Kline_point_arr.append( (x , y , ShangShenQuShi , HeiMoShui ))
			elif y < Kline_point_arr[-1][1] * (1 - param1 / 100.0):
				key_point_arr.append( ( Kline_point_arr[-1][0], Kline_point_arr[-1][1] , RED_LINE)) 
				Kline_point_arr.append( (x , y , ZiRanHuiChe , QianBi ))
				big_condition = ZiRanHuiChe
		elif big_condition == ZiRanHuiShen:
		elif big_condition == CiJiHuiShen:

		elif big_condition == XiaJiangQushi:

		elif big_condition == ZiRanHuiChe:
			if  y < Kline_point_arr[-1][1]:
				Kline_point_arr.append( (x , y , ZiRanHuiChe , QianBi ))
			
		elif big_condition == CiJiHuiChe:

	plt.show()

if __name__ == '__main__':
	main()