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

'''
主要函数
'''
def main():
	print "main"
	data = Future.getOneInstrumentDayBetween('RB88','1985-01-01','2017-06-23')
	#print data
	#indata = [(x[0],x[5]) for x in data]
	x_data = [datetime.datetime.strptime(x[0], '%Y-%m-%d').date()  for x in data]
	y_data = [x[5] * 1.0 for x in data]
	#print y_data
	plt.plot(x_data, y_data)
	plt.show()

def test( canshu = 0.06 ):
	data = Future.getOneInstrumentDayBetween('RB88','2012-01-01','2013-07-31') # '2015-01-01','2016-06-23',,2013-06-01','2015-01-01 , '2016-06-23','2017-12-31'
	indata = [(x[0],x[5]) for x in data]
	llen = len(indata)
	x1_data = [datetime.datetime.strptime(x[0], '%Y-%m-%d').date()  for x in data]
	y1_data = [x[5] * 1.0 - 1000 for x in data]
	#print y_data

	ax = plt.subplot(111)
	plt.plot(x1_data, y1_data)

	new_data = []
	red_data = []

	annotate_arr = []
	if len(indata) > 2:
		direction = 0
		if indata[1][1] > indata[0][1]:
			direction = 1
		else:
			direction = -1 
		new_data.append(indata[0])
		pre_high = indata[0][1]
		pre_low  = indata[0][1]
		for i in range(1,llen):
			(d , c) = indata[i]
			if direction == 1 and c > pre_high:
				pre_high = c
				new_data.append(indata[i])
			elif direction == 1 and c < pre_high * ( 1 - canshu):
				direction = -1
				pre_low   = c
				red_data.append(new_data[-1])
				new_data.append(indata[i])
			elif direction == -1 and c < pre_low:
				pre_low  = c
				new_data.append(indata[i])
			elif direction == -1 and c > pre_low * (1 + canshu):
				direction = 1
				pre_high = c
				red_data.append(new_data[-1])
				new_data.append(indata[i])

		x_data = [datetime.datetime.strptime(x[0], '%Y-%m-%d').date()  for x in new_data]
		y_data = [x[1] * 1.0 for x in new_data]

		x2_data = [datetime.datetime.strptime(x[0], '%Y-%m-%d').date()  for x in red_data]
		y2_data = [x[1] * 1.0 for x in red_data]
		#print x2_data
		#print y2_data
		print len(x2_data) , len(y2_data)
		plt.plot(x_data, y_data )
		plt.plot(x_data, y_data , 'ks')
		plt.plot(x2_data , y2_data , 'r-o')
		for d in annotate_arr:
			plt.annotate("tp", xy=d )
		plt.show()

# livermore 曲线图
if __name__ == '__main__':
	#main()
	test()