# -*- coding: utf-8 -*-
#
# Copyright 2017  Inc
# @author ipqhjjybj 

import sys
import os
import six
import numpy as np
import pandas as pd
from rqalpha.utils.config import *
from rqalpha.data.base_data_source import BaseDataSource

sys.path.append("..")

from spider.stock import *
from spider.future import *

import matplotlib.pyplot as plt  
import datetime


MainShangShen  = "主-上升趋势".decode('utf-8')
MainXiaJiang   = "主-下降趋势".decode('utf-8')

ShangShenQuShi = "上升趋势".decode('utf-8')
ZiRanHuiShen   = "自然回升".decode('utf-8')
CiJiHuiShen    = "次级回升".decode('utf-8')

XiaJiangQushi  = "下降趋势".decode('utf-8')
ZiRanHuiChe    = "自然回撤".decode('utf-8')
CiJiHuiChe     = "次级回撤".decode('utf-8')

HeiMoShui      = "k"        # 上升趋势黑墨水
HongMoShui     = "r"        # 下降趋势红墨水
QianBi         = "b"		# 其他栏 铅笔

NoBelowLine    = ""			# 没有下划线 
RedBelowLine   = "r"        # 有红色的下划线
BlackBelowLine = "b"        # 有黑色的下划线

RED_LINE       = "r"        # 上升趋势以及自然回调后的点下标记
BLACK_LINE     = "b"        # 下降趋势以及自然回升形成的点下标记

TimeWindow     =  4 		# 保留最近4个关键点
'''
liverMoreStrategy 的初始化
'''
class LiverMoreStrategy():

	'''
	初始化, testData = [(datetime)]
	'''
	def __init__(self , testData = []):
		print "init livermoreStrategy"
		self.keyPointArr   = [] # 存储最重要的几个关键点，  (点位,时间, 线的颜色)的格式
		self.KLinePointArr = [] # [(datetime,Y,"上升趋势",'r')] 存储剩下的趋势点, 上升趋势黑墨水 k--black，下降趋势红墨水 ， 其他栏的点，铅笔
		self.QuJianPairs   = [] # [( (x1,y1),(x2,y2),big_condition)]记录两个点形成的区间及其意义

		self.number_ssqs   = [] # 上升趋势
		self.number_zrhs   = [] # 自然回升
		self.number_cjhs   = [] # 次级回升
		self.number_xjqs   = [] # 下降趋势
		self.number_zrhc   = [] # 自然回撤
		self.number_cjhc   = [] # 次级回撤

		self.ori_data      = testData
		self.cp_data       = [] # 对照的代码
	'''
	数字记录栏
	'''
	def addToNumberFigure(self, datetime_s , number, i_condition):
		if i_condition == ShangShenQuShi:
			self.number_ssqs.append( (datetime_s, number , NoBelowLine))
		if i_condition == ZiRanHuiShen:
			self.number_zrhs.append( (datetime_s, number , NoBelowLine))
		if i_condition == CiJiHuiShen:
			self.number_cjhs.append( (datetime_s, number , NoBelowLine))
		if i_condition == XiaJiangQushi:
			self.number_xjqs.append( (datetime_s, number , NoBelowLine))
		if i_condition == ZiRanHuiChe:
			self.number_zrhc.append( (datetime_s, number , NoBelowLine))
		if i_condition == CiJiHuiChe :
			self.number_cjhc.append( (datetime_s, number , NoBelowLine))

		color = QianBi
		if i_condition == ShangShenQuShi:
			color = HeiMoShui
		if i_condition == XiaJiangQushi:
			color = HongMoShui
		self.KLinePointArr.append( (datetime_s, number , i_condition , color))

	def getPreLine(self, param1 = 6 , param2 = 3):
		self.cp_data.append( (self.ori_data[0][0] , self.ori_data[0][1]))
		dirction = 1
		if self.ori_data[1][1] < self.ori_data[0][1]:
			dirction = -1
		for i in range(1, len(self.ori_data)):
			(x,y)   = self.ori_data[i]
			(px,py) = self.cp_data[-1]
			if dirction == 1:
				if y > py:
					self.cp_data.append( (x,y))
				elif y < py * ( 1 - param1 / 100.0):
					dirction = -1
					self.cp_data.append( (x,y))
			if dirction == -1:
				if y < py:
					self.cp_data.append( (x,y))
				elif y > py * ( 1 + param1 / 100.0):
					self.cp_data.append( (x,y))

	'''
	判断下降趋势
	'''
	def judge_xjqs(self , big_condition ,  y , param2):
		if len(self.number_xjqs) > 0:
			if y < self.number_xjqs[-1][1]:
				big_condition = XiaJiangQushi
		if len(self.number_zrhc) > 0:
			for i in range(1 , len(self.number_zrhc) + 1):
				if self.number_zrhc[-i][2] == RED_LINE and y < self.number_zrhc[-i][1] * ( 1 - param2 / 100.0):
					big_condition = XiaJiangQushi
		return big_condition
	'''
	判断上升趋势
	'''
	def judge_ssqs(self , big_condition ,  y , param2):
		if len(self.number_ssqs) > 0:
			if y > self.number_ssqs[-1][1]:
				print "judge ssqs:" + str(y) + "  " + str(self.number_ssqs[-1][0]) + "  " + str(self.number_ssqs[-1][1]) + "  " + str(self.number_ssqs[-1][2]) 
				big_condition = ShangShenQuShi
		if len(self.number_zrhs) > 0:
			for i in range(1 , len(self.number_zrhs) + 1):
				if self.number_zrhs[-i][2] == BLACK_LINE and y > self.number_zrhs[-i][1] * ( 1 + param2 / 100.0):
					big_condition = ShangShenQuShi
		return big_condition
	'''
	获得新的K线
	'''
	def getNewKline(self , param1 = 6 , param2 = 3 ):
		big_condition = ShangShenQuShi     # 当前趋势栏
		point_color   = HeiMoShui

		start_point   = (self.ori_data[0][0] , self.ori_data[0][1] )
		if self.ori_data[1][1] > self.ori_data[0][1]:
			big_condition = XiaJiangQushi
			point_color   = HongMoShui

		#self.KLinePointArr.append( (self.ori_data[0][0] , self.ori_data[0][1] , big_condition , point_color))
		self.addToNumberFigure( self.ori_data[0][0] , self.ori_data[0][1] , big_condition)

		for i in range(1, len(self.ori_data)):
			(pl_x,pl_y,pl_condition,pl_color) = self.KLinePointArr[-1]
			(x,y) = self.ori_data[i]
			print "big_condition"+big_condition
			print pl_x.strftime("%Y-%m-%d"),pl_y,pl_condition,pl_color
			print x.strftime("%Y-%m-%d"),y
			if big_condition == ShangShenQuShi:
				print "t1:" + ShangShenQuShi
				if y > pl_y:
					self.addToNumberFigure( x , y , big_condition) # 上升趋势延续，黑墨水描绘
				elif y < pl_y * (1 - param1 / 100.0):
					# 上个区间结束
					self.QuJianPairs.append( (start_point, (pl_x,pl_y) , big_condition)) 
					self.keyPointArr.append( (pl_x,pl_y,RED_LINE))
					self.number_ssqs[-1] = (self.number_ssqs[-1][0] , self.number_ssqs[-1][1] , RED_LINE)
					# 下个区间开始
					big_condition = ZiRanHuiChe
					start_point = (x,y)
					self.addToNumberFigure( x , y ,big_condition)
			elif big_condition == ZiRanHuiShen:
				print "t2:" + ZiRanHuiShen 
				if y > pl_y:
					print "y > pl_y"
					# 自然回升转 上升趋势
					# 1、大于上升趋势的最后一个点
					# 2、大于最近的带有黑色线的自然上升点
					big_condition = self.judge_ssqs(big_condition , y , param2)
					self.addToNumberFigure(x , y, big_condition)
				elif y < pl_y * (1 - param1 / 100.0):
					print "y < pl_y * (1 - param1 / 100.0) y: "  + str(y) + "  < " + str(pl_y * (1 - param1 / 100.0) )
					self.QuJianPairs.append( (start_point , (pl_x,pl_y) , big_condition))
					self.keyPointArr.append( (pl_x , pl_y , BLACK_LINE))
					self.number_zrhs[-1] = (self.number_zrhs[-1][0] , self.number_zrhs[-1][1] , BLACK_LINE)
					#开启下一个状态
					big_condition = ZiRanHuiChe
					start_point = (x,y)
					# 自然回升转自然回撤
					# 自然回升转下降趋势
					# 当前点小于下降趋势的最后一个点 或 小于带红线的自然回撤最后一个点
					big_condition = self.judge_xjqs(big_condition , y , param2)
					# 自然回升转次级回撤
					# 当前价格 > 自然回撤的最后一个价格时，为次级回撤
					if len(self.number_zrhc) > 0 and y > self.number_zrhc[-1][1]:
						big_condition = CiJiHuiChe
					if len(self.number_zrhc) == 0:
						big_condition = ZiRanHuiChe
					self.addToNumberFigure(x, y , big_condition)
			elif big_condition == CiJiHuiShen:
				print "t3:" + CiJiHuiShen 
				if y > pl_y:
					#判断次级回升上升为自然回升
					if len(self.number_zrhs) > 0 and y > self.number_zrhs[-1][1]:
						big_condition = ZiRanHuiShen
					if len(self.number_zrhs) == 0:
						big_condition = ZiRanHuiShen
					#判断次级回升为上升趋势
					big_condition = self.judge_ssqs(big_condition, y, param2)
					self.addToNumberFigure( x , y , big_condition) # 上升趋势延续，黑墨水描绘
				elif y < pl_y * (1 - param1 / 100.0):
					#结束上一个状态
					self.QuJianPairs.append((start_point , (pl_x, pl_y) , big_condition))
					#开启下一个状态
					## 次级回升这里之后的状态。。 比较难搞，先简单定义为自然回撤
					# 如果小于自然回撤的最后一个点， 则记录在自然回撤里
					big_condition = CiJiHuiChe
					start_point = (x,y)
					#判断自然回撤
					if len(self.number_zrhc) > 0 and y < self.number_zrhc[-1][1]:
						big_condition = ZiRanHuiChe
					if len(self.number_zrhc) == 0:
						big_condition = ZiRanHuiChe
					#判断下降趋势
					big_condition = self.judge_xjqs(big_condition, y, param2)
					self.addToNumberFigure(x , y, big_condition)
					## 向下
			elif big_condition == XiaJiangQushi:
				print "t4:" + big_condition
				if y < pl_y:
					self.addToNumberFigure( x , y , big_condition)
				elif y > pl_y * (1 + param1 / 100.0):
					# 上个区间结束
					self.QuJianPairs.append( (start_point, (pl_x,pl_y) , big_condition))
					self.keyPointArr.append( (pl_x,pl_y, BLACK_LINE))
					self.number_xjqs[-1] = (self.number_xjqs[-1][0], self.number_xjqs[-1][1], BLACK_LINE)
					# 下个区间开始
					big_condition = ZiRanHuiShen
					start_point = (x,y)
					self.addToNumberFigure( x , y , big_condition)
			elif big_condition == ZiRanHuiChe:
				print "t5:" + big_condition
				if y < pl_y:
					# 自然回撤转下降趋势
					big_condition = self.judge_xjqs(big_condition , y , param2)
					self.addToNumberFigure( x , y, big_condition)
				elif y > pl_y * (1 + param1 / 100.0):
					# 结束上一个状态
					self.QuJianPairs.append( (start_point, (pl_x , pl_y) , big_condition))
					self.keyPointArr.append( (pl_x , pl_y ,RED_LINE))
					self.number_zrhc[-1] = (self.number_zrhc[-1][0] , self.number_zrhc[-1][1] , RED_LINE)
					# 开启下一个状态
					big_condition = ZiRanHuiShen
					start_point = (x,y)
					# 判断是否是次级回升
					if len(self.number_zrhs) > 0 and y < self.number_zrhs[-1][1]:
						big_condition = CiJiHuiShen
						print self.number_zrhs
					if len(self.number_zrhs) == 0:
						big_condition = ZiRanHuiShen
					# 判断是否是上升趋势 , 
					big_condition = self.judge_ssqs(big_condition ,y ,param2)
					self.addToNumberFigure( x, y , big_condition)
			elif big_condition == CiJiHuiChe:
				print "t6:" + big_condition
				if y < pl_y:
					##次级回撤变为自然回撤
					if len(self.number_zrhc) > 0 and y < self.number_zrhc[-1][1]:
						big_condition = ZiRanHuiChe
					if len(self.number_zrhc) == 0:
						big_condition = ZiRanHuiChe
					# 次级回撤转下降趋势
					big_condition = self.judge_xjqs(big_condition , y, param2)
					self.addToNumberFigure( x, y , big_condition)
				elif y > pl_y * (1 + param1 / 100.0):
					# 上个区间结束
					self.QuJianPairs.append( (start_point, (pl_x,pl_y) , big_condition))
					#开启下一个状态
					## 次级回撤这里之后的状态。。 比较难搞，先简单定义为自然回升
					big_condition = CiJiHuiShen
					start_point = (x,y)
					#判断是否是自然回升
					if len(self.number_zrhs) > 0 and y > self.number_zrhs[-1][1]:
						big_condition = ZiRanHuiShen
					if len(self.number_zrhs) == 0:
						big_condition = ZiRanHuiShen
					# 判断是否是上升趋势 , 
					big_condition = self.judge_ssqs(big_condition , y , param2)
					self.addToNumberFigure(x , y ,big_condition)
	'''
	画图并展示
	vlines(x, ymin, ymax)
	hlines(y, xmin, xmax)  
	'''
	def plotFigure(self):
		print "plotFigure"
		xx = []
		yy = []
		for (x,y) in self.cp_data:
			xx.append(x)
			yy.append(y+1000)
		plt.scatter(xx , yy) 
		xx = []
		yy = []
		for (x , y) in self.ori_data:
			xx.append(x)
			yy.append(y-1000)
		#print y
		plt.plot(xx , yy) 
		#print self.KLinePointArr

		x1 = [x[0] for x in self.KLinePointArr if x[3] == HeiMoShui]
		y1 = [x[1] for x in self.KLinePointArr if x[3] == HeiMoShui]
		
		plt.scatter(x1, y1 , c = HeiMoShui , marker = 's')


		x1 = [x[0] for x in self.KLinePointArr if x[3] == HongMoShui]
		y1 = [x[1] for x in self.KLinePointArr if x[3] == HongMoShui]
		plt.scatter(x1, y1 , c = HongMoShui , marker = 's')

		x1 = [x[0] for x in self.KLinePointArr if x[3] == QianBi]
		y1 = [x[1] for x in self.KLinePointArr if x[3] == QianBi]
		plt.scatter(x1, y1 , c = QianBi , marker = 'x')

		#print self.keyPointArr
		for (xx,yy,ccolor) in self.keyPointArr:
			x = [xx - datetime.timedelta(days=15) , xx + datetime.timedelta(days=15)]
			y = [yy,yy]
			#plt.plot(x , y, color = ccolor) 
			plt.hlines( y[0], x[0], x[1] , colors = ccolor , linestyles = "dashed")

		plt.show()

def test():
	data = Future.getOneInstrumentDayBetween('RB88','2013-12-01','2016-07-31') # '2015-01-01','2016-06-23',,2013-06-01','2015-01-01 , '2016-06-23','2017-12-31'
	data = [ (datetime.datetime.strptime(x[0], '%Y-%m-%d'), x[5]) for x in data]

	#print data[:3]
	st = LiverMoreStrategy( testData = data)

	st.getPreLine(param1 = 6 , param2 = 1.5)
	st.getNewKline(param1 = 6 , param2 = 1.5)
	st.plotFigure()

if __name__ == '__main__':
	#main()
	test()