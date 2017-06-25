# encoding: UTF-8

"""
绘制livermore的图
"""

from MongodbClient import *
import matplotlib.pyplot as plt

condition_type = ["次级回升","自然回升","上升趋势","下降趋势","自然回撤","次级回撤"]
condition_type = [x.decode('utf-8') for x in condition_type]

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


key_point_arr = [] 						# 存储最重要的几个关键点，  (点位,时间)的格式
K_point_arr   = []						# [(datetime,Y,'r')] 存储剩下的趋势点, 上升趋势黑墨水 k--black，下降趋势红墨水 ， 其他栏的点，铅笔

def main():
	data = MongoClient.getBetweenClose("VnTrader_1Min_Db","hc1710",'2017-06-01','2017-08-24')
	big_condition = "上升趋势"
	point_color   = "k"
	if data[1][1] > data[0][1]:
		big_condition = "下降趋势" 
		point_color   = "r"
	for (d1 , c1) in data:
		
	plt.show()

if __name__ == '__main__':
	main()