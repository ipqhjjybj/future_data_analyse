# encoding: UTF-8

"""
本模块中主要包含：
1. 从通联数据下载历史行情的引擎
2. 用来把MultiCharts导出的历史数据载入到MongoDB中用的函数
3. 增加从通达信导出的历史数据载入到MongoDB中的函数
"""


from datetime import datetime, timedelta
from time import time
from multiprocessing.pool import ThreadPool

import pymongo

import numpy as np
import matplotlib.pyplot as plt

mongoHost = 'localhost'
mongoPort = 27017

class MongoClient():

	__dbClient = None
	'''
	获得Mongo连接单例
	'''
	@staticmethod
	def getMongoInstance():
		if MongoClient.__dbClient == None:
			MongoClient.__dbClient = pymongo.MongoClient( mongoHost , mongoPort)
		return MongoClient.__dbClient

	'''
	获得dbclient
	'''
	@staticmethod
	def getBetweenData(db_name,table_name, start_date , end_date ):
		client = MongoClient.getMongoInstance()
		db = client[db_name]
		collection_useraction = db[table_name]

		s1 = datetime.strptime(start_date , '%Y-%m-%d')
		s2 = datetime.strptime(end_date , '%Y-%m-%d')

		c1 = collection_useraction.find({'datetime':{"$gte":s1,"$lte":s2}})
		dic = {}
		for c in c1:
			#print c
			#print type(c)
			key = c["date"] + " " + c["time"]
			key = datetime.strptime(key , '%Y%m%d %H:%M:%S')
			dic[key] = c
		return dic
	'''
	获得 相减数据
	'''
	@staticmethod
	def getMinusData(db_name, table_name1 , table_name2 , start_date , end_date):
		data_c1 = MongoClient.getBetweenData(db_name , table_name1 , start_date ,end_date)
		data_c2 = MongoClient.getBetweenData(db_name , table_name2 , start_date ,end_date)

		union_dates = [x for x in data_c1.keys() if x in data_c2.keys()]
		union_dates.sort()
		arr   = []
		arr_1 = []
		arr_2 = []
		for t_date in union_dates:
			minus_close = data_c1[t_date]["close"] - data_c2[t_date]["close"]
			arr_1.append( (t_date , data_c1[t_date]["close"]))
			arr_2.append( (t_date , data_c2[t_date]["close"]))
			arr.append( (t_date , minus_close + 3000))
		return arr , arr_1 , arr_2

if __name__ == '__main__':

	mgclient = MongoClient.getMongoInstance()

	data = MongoClient.getBetweenData("VnTrader_1Min_Db","hc1710",'2017-01-01','2017-08-24')
	
	(data, data_c1 , data_c2)  = MongoClient.getMinusData("VnTrader_1Min_Db","hc1710","rb1710",'2017-06-01','2017-06-24')
	
	xd = [x[0] for x in data]
	yd = [x[1] for x in data]

	xd_c1 = [x[0] for x in data_c1]
	yd_c1 = [x[1] for x in data_c1]

	xd_c2 = [x[0] for x in data_c2]
	yd_c2 = [x[1] for x in data_c2]

	plt.plot(xd,yd , label="minus", color="red",linewidth=3)
	plt.plot(xd_c1 , yd_c1)
	plt.plot(xd_c2 , yd_c2)
	plt.show()