# encoding: UTF-8

"""
对于两个品种进行做差分析
"""

from MongodbClient import *
'''
对两个品种做差并画图
'''
def test1( database_name = "VnTrader_1Min_Db" , symbol1 = "hc1710" , symbol2 = "rb1710" , start_date = '2017-03-01' ,end_date = '2017-06-24', show_compare = True):
	mgclient = MongoClient.getMongoInstance()
	
	(data, data_c1 , data_c2)  = MongoClient.getMinusData(database_name, symbol1, symbol2, start_date, end_date)
	
	xd = [x[0] for x in data]
	yd = [x[1] for x in data]

	xd_c1 = [x[0] for x in data_c1]
	yd_c1 = [x[1] for x in data_c1]

	xd_c2 = [x[0] for x in data_c2]
	yd_c2 = [x[1] for x in data_c2]

	plt.plot(xd,yd , label="minus", color="red",linewidth=3)
	if True == show_compare:
		plt.plot(xd_c1 , yd_c1)
		plt.plot(xd_c2 , yd_c2)
	plt.show()

if __name__ == '__main__':
	test1(symbol1 = 'ih888' , symbol2 = 'if888' , show_compare = False)
	#test1(symbol1 = 'if1707' , symbol2 = 'ih1707' , show_compare = False)
	#test1(symbol1 = 'pp1709' , symbol2 = 'hc1710' , show_compare = False)
	#test1(symbol1 = 'rb1710' , symbol2 = 'hc1710' , show_compare = False)
	#test1(symbol1 = 'rb888' , symbol2 = 'hc888' , show_compare = False)
	#test1(symbol1 = 'if1707' , symbol2 = 'if1709' , show_compare = False)