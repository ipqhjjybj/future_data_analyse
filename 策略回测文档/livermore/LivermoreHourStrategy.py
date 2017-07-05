# encoding: UTF-8

# 重载sys模块，设置默认字符串编码方式为utf8
import sys
reload(sys)
sys.setdefaultencoding('utf8')

# vn.trader模块
from vnpy.event import EventEngine
from vnpy.trader.vtEngine import MainEngine
from vnpy.trader.uiQt import qApp
from vnpy.trader.uiMainWindow import MainWindow

# 加载底层接口
from vnpy.trader.gateway import ctpGateway

# 加载上层应用
from vnpy.trader.app import riskManager, ctaStrategy

from vnpy.trader.app.ctaStrategy.ctaHistoryData import *



import talib
import numpy as np

import talib
import numpy as np

from vnpy.trader.vtObject import VtBarData
from vnpy.trader.vtConstant import EMPTY_STRING
from vnpy.trader.app.ctaStrategy.ctaTemplate import CtaTemplate

from vnpy.trader.app.ctaStrategy.ctaBacktesting import *
from PyQt4 import QtCore, QtGui

ShangShenQuShi = "上升趋势".decode('utf-8')
ZiRanHuiShen   = "自然回升".decode('utf-8')
CiJiHuiShen    = "次级回升".decode('utf-8')

XiaJiangQushi  = "下降趋势".decode('utf-8')
ZiRanHuiChe    = "自然回撤".decode('utf-8')
CiJiHuiChe     = "次级回撤".decode('utf-8')

HeiMoShui      = "k"        # 上升趋势黑墨水
HongMoShui     = "r"        # 下降趋势红墨水
QianBi         = "b"        # 其他栏 铅笔

NoBelowLine    = ""         # 没有下划线 
RED_LINE       = "r"        # 上升趋势以及自然回调后的点下标记
BLACK_LINE     = "b"        # 下降趋势以及自然回升形成的点下标记

'''
livermore 策略
'''
##################################################################

class LivermoreHourStrategy(CtaTemplate):
    """基于livermore策略的交易策略"""

    className = 'LivermoreHourStrategy'
    author = u'ipqhjjybj'

    # 策略参数
    param1 = 6                  # 每次变化 param1 画K线的数
    param2 = 3                  # 突破 param2 多少确定趋势

    zhangDiePoint = 10          # 涨跌多少点开多开空


    # 策略变量
    bar = None                  # 1分钟K线对象
    barMinute = EMPTY_STRING    # K线当前的分钟
    fiveBar = None              # 1分钟K线对象

    bufferSize = 100                    # 需要缓存的数据的大小
    bufferCount = 0                     # 目前已经缓存了的数据的计数
    initDays = 10                       # 初始化数据所用的天数
    fixedSize = 1                       # 每次交易的数量

    buyOrderID = None                   # OCO委托买入开仓的委托号
    shortOrderID = None                 # OCO委托卖出开仓的委托号
    limitOrderList = []                 # 保存限价委托代码的列表
    stopOrderList = []                  # 保存停止委托单代码的列表

    #highArray = np.zeros(bufferSize)     # K线最高价的数组
    #lowArray = np.zeros(bufferSize)      # K线最低价的数组
    closeArray = np.zeros(bufferSize)     # K线收盘价的数组

    conditionArray = np.zeros(bufferSize) # 市场状态数组

    keyPointArr   = []                    # 存储最重要的几个关键点，  (点位,时间, 线的颜色)的格式
    KLinePointArr = []                    # [(datetime,Y,"上升趋势",'r')] 存储剩下的趋势点, 上升趋势黑墨水 k--black，下降趋势红墨水 ， 其他栏的点，铅笔

    number_ssqs   = []                    # 上升趋势
    number_zrhs   = []                    # 自然回升
    number_cjhs   = []                    # 次级回升
    number_xjqs   = []                    # 下降趋势
    number_zrhc   = []                    # 自然回撤
    number_cjhc   = []                    # 次级回撤

    QuJianPairs   = []                    # 区间对

    big_condArray = [0]                   # 大方向状态

    conditionChangeType = 0               # 状态变更的原因 
    # 突破上升趋势最大点 --> 1
    # W形上升趋势--> 2
    # 突破下降趋势最低点 --> 3
    # 倒W形下降趋势 --> 4

    ori_data      = [(0,0)]* bufferSize   # 原始的数据  [(datetime , close_price)]
    #cp_data       = []                   # 用来对照 对照的代码

    # 参数列表，保存了参数的名称
    paramList = ['name',
                 'className',
                 'author',
                 'vtSymbol',
                 ]    

    # 变量列表，保存了变量的名称
    varList = ['inited',
               'trading',
               'pos',
               'param1',
               'param2',]  

    #----------------------------------------------------------------------
    def __init__(self, ctaEngine, setting):
        """Constructor"""
        super(LivermoreHourStrategy, self).__init__(ctaEngine, setting)

        for key in setting.keys():
            if key == "param1":
                self.param1 = setting[key]
            if key == "param2":
                self.param2 = setting[key]

                
        #print setting
    #----------------------------------------------------------------------
    def onInit(self):
        """初始化策略（必须由用户继承实现）"""
        self.writeCtaLog(u'%s策略初始化' %self.name)
        
        # 载入历史数据，并采用回放计算的方式初始化策略数值
        initData = self.loadBar(self.initDays)
        for bar in initData:
            self.onBar(bar)

        print self.param1 , self.param2
        self.keyPointArr   = [] # 存储最重要的几个关键点，  (点位,时间, 线的颜色)的格式
        self.KLinePointArr = [] # [(datetime,Y,"上升趋势",'r')] 存储剩下的趋势点, 上升趋势黑墨水 k--black，下降趋势红墨水 ， 其他栏的点，铅笔
        self.number_ssqs   = [] # 上升趋势
        self.number_zrhs   = [] # 自然回升
        self.number_cjhs   = [] # 次级回升
        self.number_xjqs   = [] # 下降趋势
        self.number_zrhc   = [] # 自然回撤
        self.number_cjhc   = [] # 次级回撤

        self.putEvent()

    #----------------------------------------------------------------------
    def onStart(self):
        """启动策略（必须由用户继承实现）"""
        self.writeCtaLog(u'%s策略启动' %self.name)
        self.putEvent()

    #----------------------------------------------------------------------
    def onStop(self):
        """停止策略（必须由用户继承实现）"""
        self.writeCtaLog(u'%s策略停止' %self.name)
        self.putEvent()

    #----------------------------------------------------------------------
    def onTick(self, tick):
        """收到行情TICK推送（必须由用户继承实现）"""
        # 聚合为1分钟K线
        tickMinute = tick.datetime.minute

        if tickMinute != self.barMinute:  
            if self.bar:
                self.onBar(self.bar)

            bar = VtBarData()              
            bar.vtSymbol = tick.vtSymbol
            bar.symbol = tick.symbol
            bar.exchange = tick.exchange

            bar.open = tick.lastPrice
            bar.high = tick.lastPrice
            bar.low = tick.lastPrice
            bar.close = tick.lastPrice

            bar.date = tick.date
            bar.time = tick.time
            bar.datetime = tick.datetime    # K线的时间设为第一个Tick的时间

            self.bar = bar                  # 这种写法为了减少一层访问，加快速度
            self.barMinute = tickMinute     # 更新当前的分钟
        else:                               # 否则继续累加新的K线
            bar = self.bar                  # 写法同样为了加快速度

            bar.high = max(bar.high, tick.lastPrice)
            bar.low = min(bar.low, tick.lastPrice)
            bar.close = tick.lastPrice

    #----------------------------------------------------------------------
    def onBar(self, bar):
        """收到Bar推送（必须由用户继承实现）"""
        self.onFiveBar(bar)
        # 如果当前是一个5分钟走完
        # if bar.datetime.minute % 5 == 0:
        #     # 如果已经有聚合5分钟K线
        #     if self.fiveBar:
        #         # 将最新分钟的数据更新到目前5分钟线中
        #         fiveBar = self.fiveBar
        #         fiveBar.high = max(fiveBar.high, bar.high)
        #         fiveBar.low = min(fiveBar.low, bar.low)
        #         fiveBar.close = bar.close
                
        #         # 推送5分钟线数据
        #         self.onFiveBar(fiveBar)
                
        #         # 清空5分钟线数据缓存
        #         self.fiveBar = None
        # else:
        #     # 如果没有缓存则新建
        #     if not self.fiveBar:
        #         fiveBar = VtBarData()
                
        #         fiveBar.vtSymbol = bar.vtSymbol
        #         fiveBar.symbol = bar.symbol
        #         fiveBar.exchange = bar.exchange
            
        #         fiveBar.open = bar.open
        #         fiveBar.high = bar.high
        #         fiveBar.low = bar.low
        #         fiveBar.close = bar.close
            
        #         fiveBar.date = bar.date
        #         fiveBar.time = bar.time
        #         fiveBar.datetime = bar.datetime 
                
        #         self.fiveBar = fiveBar
        #     else:
        #         fiveBar = self.fiveBar
        #         fiveBar.high = max(fiveBar.high, bar.high)
        #         fiveBar.low = min(fiveBar.low, bar.low)
        #         fiveBar.close = bar.close
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
    '''
    判断下降趋势
    '''
    def judge_xjqs(self , big_condition ,  y , param2):
        if len(self.number_xjqs) > 0:
            if y < self.number_xjqs[-1][1]:
                self.conditionChangeType = 3
                big_condition = XiaJiangQushi
        to_drop_line = 0
        if len(self.number_zrhc) > 0:
            for i in range(1 , len(self.number_zrhc) + 1):
                if self.number_zrhc[-i][2] == RED_LINE :
                    if y < self.number_zrhc[-i][1] - param2 :
                        self.conditionChangeType = 4
                        big_condition = XiaJiangQushi
                        to_drop_line = 1
                    break
        if 1 == to_drop_line:
            for i in range(1 , len(self.number_zrhc) + 1):
                if self.number_zrhc[-i][2] == RED_LINE:
                    self.number_zrhc[-i] = ( self.number_zrhc[-i][0] , self.number_zrhc[-i][1], NoBelowLine)
        return big_condition
    '''
    判断上升趋势
    '''
    def judge_ssqs(self , big_condition ,  y , param2):
        if len(self.number_ssqs) > 0:
            if y > self.number_ssqs[-1][1]:
                #print "judge ssqs:" + str(y) + "  " + str(self.number_ssqs[-1][0]) + "  " + str(self.number_ssqs[-1][1]) + "  " + str(self.number_ssqs[-1][2]) 
                self.conditionChangeType = 1
                big_condition = ShangShenQuShi
        to_drop_line = 0
        if len(self.number_zrhs) > 0:
            for i in range(1 , len(self.number_zrhs) + 1):
                if self.number_zrhs[-i][2] == BLACK_LINE :
                    if y > self.number_zrhs[-i][1] + param2 :
                        self.conditionChangeType = 2
                        big_condition = ShangShenQuShi
                        to_drop_line = 1
                    break
        if 1 == to_drop_line:
            for i in range(1 , len(self.number_zrhs) + 1):
                if self.number_zrhs[-i][2] == BLACK_LINE:
                    self.number_zrhs[-i] = (self.number_zrhs[-i][0] , self.number_zrhs[-i][1] , NoBelowLine) 
                    #self.number_zrhs[-i][2] = NoBelowLine
        return big_condition

    # livermore 策略 核心判断函数
    def judge(self, t_klinePoint , t_ori_data):
        (pl_x, pl_y , pl_condition , pl_color) = t_klinePoint
        (x,y) = t_ori_data
        if self.big_condition == ShangShenQuShi:
            if y > pl_y:
                self.addToNumberFigure( x , y , self.big_condition) # 上升趋势延续，黑墨水描绘
            elif y < pl_y  - self.param1 :
                #上个区间结束
                self.QuJianPairs.append( (self.start_point, (pl_x,pl_y) , self.big_condition)) 
                self.keyPointArr.append( (pl_x,pl_y,RED_LINE))
                self.number_ssqs[-1] = (self.number_ssqs[-1][0] , self.number_ssqs[-1][1] , RED_LINE)
                # 下个区间开始
                self.big_condition = ZiRanHuiChe
                self.start_point = (x,y)
                self.addToNumberFigure( x , y ,self.big_condition)
        elif self.big_condition == ZiRanHuiShen:
            if y > pl_y:
                # 自然回升转 上升趋势
                # 1、大于上升趋势的最后一个点
                # 2、大于最近的带有黑色线的自然上升点
                self.big_condition = self.judge_ssqs(self.big_condition , y , self.param2)
                self.addToNumberFigure(x , y, self.big_condition)
            elif y < pl_y - self.param1 :

                self.QuJianPairs.append( (self.start_point , (pl_x,pl_y) , self.big_condition))
                self.keyPointArr.append( (pl_x , pl_y , BLACK_LINE))
                self.number_zrhs[-1] = (self.number_zrhs[-1][0] , self.number_zrhs[-1][1] , BLACK_LINE)
                #开启下一个状态
                # 自然回升转自然回撤
                self.big_condition = ZiRanHuiChe
                self.start_point = (x,y)
                # 自然回升转次级回撤
                # 当前价格 > 自然回撤的最后一个价格时，为次级回撤
                if len(self.number_zrhc) > 0 and y > self.number_zrhc[-1][1]:
                    self.big_condition = CiJiHuiChe
                if len(self.number_zrhc) == 0:
                    self.big_condition = ZiRanHuiChe
                # 自然回升转下降趋势
                # 当前点小于下降趋势的最后一个点 或 小于带红线的自然回撤最后一个点
                self.big_condition = self.judge_xjqs(self.big_condition , y , self.param2)
                self.addToNumberFigure(x, y , self.big_condition)
        elif self.big_condition == CiJiHuiShen:
            if y > pl_y:
                #判断次级回升上升为自然回升
                if len(self.number_zrhs) > 0 and y > self.number_zrhs[-1][1]:
                    self.big_condition = ZiRanHuiShen
                if len(self.number_zrhs) == 0:
                    self.big_condition = ZiRanHuiShen
                #判断次级回升为上升趋势
                self.big_condition = self.judge_ssqs(self.big_condition, y, self.param2)
                self.addToNumberFigure( x , y , self.big_condition) # 上升趋势延续，黑墨水描绘
            elif y < pl_y - self.param1 :
                #结束上一个状态
                self.QuJianPairs.append((self.start_point , (pl_x, pl_y) , self.big_condition))
                #开启下一个状态
                ## 次级回升这里之后的状态。。 比较难搞，先简单定义为自然回撤
                # 如果小于自然回撤的最后一个点， 则记录在自然回撤里
                self.big_condition = CiJiHuiChe
                self.start_point = (x,y)
                #判断自然回撤
                if len(self.number_zrhc) > 0 and y < self.number_zrhc[-1][1]:
                    self.big_condition = ZiRanHuiChe
                if len(self.number_zrhc) == 0:
                    self.big_condition = ZiRanHuiChe
                #判断下降趋势
                self.big_condition = self.judge_xjqs(self.big_condition, y, self.param2)
                self.addToNumberFigure(x , y, self.big_condition)
                ## 向下
        elif self.big_condition == XiaJiangQushi:
            if y < pl_y:
                self.addToNumberFigure( x , y , self.big_condition)
            elif y > pl_y + self.param1 :
                # 上个区间结束
                self.QuJianPairs.append( (self.start_point, (pl_x,pl_y) , self.big_condition))
                self.keyPointArr.append( (pl_x,pl_y, BLACK_LINE))
                self.number_xjqs[-1] = (self.number_xjqs[-1][0], self.number_xjqs[-1][1], BLACK_LINE)
                # 下个区间开始
                self.big_condition = ZiRanHuiShen
                self.start_point = (x,y)
                self.addToNumberFigure( x , y , self.big_condition)
        elif self.big_condition == ZiRanHuiChe:
            if y < pl_y:
                # 自然回撤转下降趋势
                self.big_condition = self.judge_xjqs(self.big_condition , y , self.param2)
                self.addToNumberFigure( x , y, self.big_condition)
            elif y > pl_y + self.param1 :
                # 结束上一个状态
                self.QuJianPairs.append( (self.start_point, (pl_x , pl_y) , self.big_condition))
                self.keyPointArr.append( (pl_x , pl_y ,RED_LINE))
                self.number_zrhc[-1] = (self.number_zrhc[-1][0] , self.number_zrhc[-1][1] , RED_LINE)
                # 开启下一个状态
                self.big_condition = ZiRanHuiShen
                self.start_point = (x,y)
                # 判断是否是次级回升
                if len(self.number_zrhs) > 0 and y < self.number_zrhs[-1][1]:
                    self.big_condition = CiJiHuiShen
                    #print self.number_zrhs
                if len(self.number_zrhs) == 0:
                    self.big_condition = ZiRanHuiShen
                    # 判断是否是上升趋势 , 
                self.big_condition = self.judge_ssqs(self.big_condition ,y ,self.param2)
                self.addToNumberFigure( x, y , self.big_condition)
        elif self.big_condition == CiJiHuiChe:
            if y < pl_y:
                ##次级回撤变为自然回撤
                if len(self.number_zrhc) > 0 and y < self.number_zrhc[-1][1]:
                    self.big_condition = ZiRanHuiChe
                if len(self.number_zrhc) == 0:
                    self.big_condition = ZiRanHuiChe
                # 次级回撤转下降趋势
                self.big_condition = self.judge_xjqs(self.big_condition , y, self.param2)
                self.addToNumberFigure( x, y , self.big_condition)
            elif y > pl_y + self.param1 :
                # 上个区间结束
                self.QuJianPairs.append( (self.start_point, (pl_x,pl_y) , self.big_condition))
                #开启下一个状态
                ## 次级回撤这里之后的状态。。 比较难搞，先简单定义为自然回升
                self.big_condition = CiJiHuiShen
                self.start_point = (x,y)
                #判断是否是自然回升
                if len(self.number_zrhs) > 0 and y > self.number_zrhs[-1][1]:
                    self.big_condition = ZiRanHuiShen
                if len(self.number_zrhs) == 0:
                    self.big_condition = ZiRanHuiShen
                # 判断是否是上升趋势 , 
                self.big_condition = self.judge_ssqs(self.big_condition , y , self.param2)
                self.addToNumberFigure(x , y ,self.big_condition)
    #----------------------------------------------------------------------
    def onFiveBar(self, bar):
        """收到5分钟K线"""
        # 撤销之前发出的尚未成交的委托（包括限价单和停止单）
        for orderID in self.limitOrderList:
            self.cancelOrder(orderID)

        #print bar.close , bar.datetime
        # 保存K线数据
        self.closeArray[0:self.bufferSize-1] = self.closeArray[1:self.bufferSize]
        self.closeArray[-1] = bar.close

        self.ori_data[0:self.bufferSize-1] = self.ori_data[1:self.bufferSize]
        self.ori_data[-1]  =  (bar.datetime , bar.close)
        
        self.bufferCount += 1

        if self.bufferCount < self.bufferSize:
            return
    
        ################### 这里处理是为了防止数组占用过多数据
        self.keyPointArr   = self.keyPointArr[-30:]     # 存储最重要的几个关键点，  (点位,时间, 线的颜色)的格式
        self.KLinePointArr = self.KLinePointArr[-30:]   # [(datetime,Y,"上升趋势",'r')] 存储剩下的趋势点, 上升趋势黑墨水 k--black，下降趋势红墨水 ， 其他栏的点，铅笔
        self.number_ssqs   = self.number_ssqs[-30:]     # 上升趋势
        self.number_zrhs   = self.number_zrhs[-30:]     # 自然回升
        self.number_cjhs   = self.number_cjhs[-30:]     # 次级回升
        self.number_xjqs   = self.number_xjqs[-30:]     # 下降趋势
        self.number_zrhc   = self.number_zrhc[-30:]     # 自然回撤
        self.number_cjhc   = self.number_cjhc[-30:]     # 次级回撤

        self.big_condArray = self.big_condArray[-30:] # 高级状态
        
        if len(self.KLinePointArr) == 0:
            ## 说明数据要初始化
            self.big_condition = ShangShenQuShi
            self.point_color   = HeiMoShui

            self.start_point = (self.ori_data[0][0] , self.ori_data[0][1])
            if self.ori_data[1][1] > self.ori_data[0][1]:
                self.big_condition = XiaJiangQushi
                self.point_color   = HongMoShui

            self.addToNumberFigure( self.ori_data[0][0] , self.ori_data[0][1] , self.big_condition)

            for i in range(1, len(self.ori_data) - 1):
                self.judge( self.KLinePointArr[-1] , self.ori_data[i])

        
        self.judge(self.KLinePointArr[-1] , self.ori_data[-1])

        self.big_condArray.append(self.big_condition)

        # 判断是否要进行交易

        buy_cond  = 0
        sell_cond = 0


        # 表示状态出现改变
        # Version 1.0 ,
        if self.big_condition == ShangShenQuShi:
            buy_cond = 1
        if self.big_condition == XiaJiangQushi:
            sell_cond = 1

        if self.pos == 0:
            if buy_cond  == 1:
                orderID = self.buy(  bar.close , self.fixedSize )
                self.limitOrderList.append(orderID)
            if sell_cond == 1:
                orderID = self.short( bar.close , self.fixedSize)
                self.limitOrderList.append(orderID)

        if self.pos > 0:
            if buy_cond == 0:
                orderID = self.sell(bar.close , abs(self.pos))
                self.limitOrderList.append(orderID)
            if sell_cond == 1:
                orderID = self.short(bar.close , self.fixedSize)
                self.limitOrderList.append(orderID)

        if self.pos < 0:
            if sell_cond == 0:
                orderID = self.cover(bar.close , abs(self.pos))
                self.limitOrderList.append(orderID)
            if buy_cond == 1:
                orderID = self.buy(bar.close , self.fixedSize)
                self.limitOrderList.append(orderID)

    
        # 发出状态更新事件
        self.putEvent()        

    #----------------------------------------------------------------------
    def onOrder(self, order):
        """收到委托变化推送（必须由用户继承实现）"""
        pass

    #----------------------------------------------------------------------
    def onTrade(self, trade):
        # 多头开仓成交后，撤消空头委托
        # if self.pos > 0:
        #     self.cancelOrder(self.shortOrderID)
        #     if self.buyOrderID in self.orderList:
        #         self.orderList.remove(self.buyOrderID)
        #     if self.shortOrderID in self.orderList:
        #         self.orderList.remove(self.shortOrderID)
        # # 反之同样
        # elif self.pos < 0:
        #     self.cancelOrder(self.buyOrderID)
        #     if self.buyOrderID in self.orderList:
        #         self.orderList.remove(self.buyOrderID)
        #     if self.shortOrderID in self.orderList:
        #         self.orderList.remove(self.shortOrderID)
        # print trade
        # 发出状态更新事件
        self.putEvent()
        
    #----------------------------------------------------------------------
    def sendOcoOrder(self, buyPrice, shortPrice, volume):
        """
        发送OCO委托
        
        OCO(One Cancel Other)委托：
        1. 主要用于实现区间突破入场
        2. 包含两个方向相反的停止单
        3. 一个方向的停止单成交后会立即撤消另一个方向的
        """
        # 发送双边的停止单委托，并记录委托号
        self.buyOrderID = self.buy(buyPrice, volume, True)
        self.shortOrderID = self.short(shortPrice, volume, True)
        
        # 将委托号记录到列表中
        self.orderList.append(self.buyOrderID)
        self.orderList.append(self.shortOrderID)


if __name__ == '__main__':
    # 提供直接双击回测的功能
    # 导入PyQt4的包是为了保证matplotlib使用PyQt4而不是PySide，防止初始化出错
    
    # 创建回测引擎
    engine = BacktestingEngine()
    
    # 设置引擎的回测模式为K线
    engine.setBacktestingMode(engine.BAR_MODE)

    # 设置回测用的数据起始日期
    engine.setStartDate('20130101')
    
    # 设置产品相关参数
    engine.setSlippage(0.2)     # 股指1跳
    engine.setRate(0.3/10000)   # 万0.3
    engine.setSize(300)         # 股指合约大小 
    engine.setPriceTick(0.2)    # 股指最小价格变动       
    
    # 设置使用的历史数据库
    engine.setDatabase(MINUTE_DB_NAME, 'rb888')
    
    # 在引擎中创建策略对象
    d = {}
    engine.initStrategy(LivermoreHourStrategy, d)
    
    # 开始跑回测
    engine.runBacktesting()
    
    # 显示回测结果
    engine.showBacktestingResult()

