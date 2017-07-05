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

from vnpy.trader.vtObject import VtBarData
from vnpy.trader.vtConstant import EMPTY_STRING
from vnpy.trader.app.ctaStrategy.ctaTemplate import CtaTemplate

'''
鳄鱼线指标
'''

########################################################################
class AlligatoragainStrategy(CtaTemplate):
    """基于King Keltner通道的交易策略"""
    className = 'AlligatoragainStrategy'
    author = u'ipqhjjybj'

    # 策略参数
    CF = 5                      # 唇线周期
    CM = 5                      # 齿线周期
    CS = 13                     # 鄂线周期
    d_CF = 3                    # 唇线平移
    d_CM = 5                    # 齿线平移
    d_CS = 8                    # 鄂线平移

    N_up = 10                   # 达到一定幅度开仓
    N_down = 10                 # 

    eyu = 0                     # 鳄鱼线的持仓信号
    lots = 1                    # 开仓手数

    # 鳄鱼线开仓涨跌线          # 
    kai_up = 0                  # 
    kai_down = 0                

    # 止损参数
    zhisunlv_l = 10             # 止损参数
    zhisunlv_s = 10             # 

    # 策略变量
    bar = None                  # 1分钟K线对象
    barMinute = EMPTY_STRING    # K线当前的分钟
    fiveBar = None              # 1分钟K线对象

    bufferSize = 30                     # 需要缓存的数据的大小
    bufferCount = 0                     # 目前已经缓存了的数据的计数
    initDays =  14                      # 初始化数据的时间

    openArray = np.zeros(bufferSize)    # K线开盘价的数组
    highArray = np.zeros(bufferSize)    # K线最高价的数组
    lowArray = np.zeros(bufferSize)     # K线最低价的数组
    closeArray = np.zeros(bufferSize)   # K线收盘价的数组

    # 策略变量数组
    zui = np.zeros(bufferSize)          # 记录各个阶段的嘴
    lips_N = np.zeros(bufferSize)       # 记录bufferSize
    teeth_N = np.zeros(bufferSize)      
    croco_N = np.zeros(bufferSize)
    

    buyOrderID = None                   # OCO委托买入开仓的委托号
    shortOrderID = None                 # OCO委托卖出开仓的委托号
    orderList = []                      # 保存委托代码的列表

    # 参数列表，保存了参数的名称
    paramList = ['name',
                 'className',
                 'author',
                 'vtSymbol',
                 'kkLength',
                 'kkDev']    

    # 变量列表，保存了变量的名称
    varList = ['inited',
               'trading',
               'pos',
               'atrValue',
               'kkMid',
               'kkUp',
               'kkDown']  

    #----------------------------------------------------------------------
    def __init__(self, ctaEngine, setting):
        """Constructor"""
        super(AlligatoragainStrategy, self).__init__(ctaEngine, setting)
        
    #----------------------------------------------------------------------
    def onInit(self):
        """初始化策略（必须由用户继承实现）"""
        self.writeCtaLog(u'%s策略初始化' %self.name)
        
        # 载入历史数据，并采用回放计算的方式初始化策略数值
        initData = self.loadBar(self.initDays)
        for bar in initData:
            self.onBar(bar)

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
        # 如果当前是一个5分钟走完
        #print bar.datetime.minute
        if (bar.datetime.minute + 1) % 15 == 0:
            # 如果已经有聚合5分钟K线
            if self.fiveBar:
                # 将最新分钟的数据更新到目前5分钟线中
                fiveBar = self.fiveBar
                fiveBar.high = max(fiveBar.high, bar.high)
                fiveBar.low = min(fiveBar.low, bar.low)
                fiveBar.close = bar.close
                
                # 推送5分钟线数据
                self.onFiveBar(fiveBar)
                
                # 清空5分钟线数据缓存
                self.fiveBar = None
        else:
            # 如果没有缓存则新建
            if not self.fiveBar:
                fiveBar = VtBarData()
                
                fiveBar.vtSymbol = bar.vtSymbol
                fiveBar.symbol = bar.symbol
                fiveBar.exchange = bar.exchange
            
                fiveBar.open = bar.open
                fiveBar.high = bar.high
                fiveBar.low = bar.low
                fiveBar.close = bar.close
            
                fiveBar.date = bar.date
                fiveBar.time = bar.time
                fiveBar.datetime = bar.datetime 
                
                self.fiveBar = fiveBar
            else:
                fiveBar = self.fiveBar
                fiveBar.high = max(fiveBar.high, bar.high)
                fiveBar.low = min(fiveBar.low, bar.low)
                fiveBar.close = bar.close
    
    #----------------------------------------------------------------------
    def onFiveBar(self, bar):
        """收到5分钟K线"""
        # 撤销之前发出的尚未成交的委托（包括限价单和停止单）
        for orderID in self.orderList:
            self.cancelOrder(orderID)

        #print bar.datetime, bar.open , bar.high, bar.low , bar.close 
        self.orderList = []
    
        # 保存K线数据
        self.openArray[0:self.bufferSize-1] = self.openArray[1:self.bufferSize]
        self.closeArray[0:self.bufferSize-1] = self.closeArray[1:self.bufferSize]
        self.highArray[0:self.bufferSize-1] = self.highArray[1:self.bufferSize]
        self.lowArray[0:self.bufferSize-1] = self.lowArray[1:self.bufferSize]

        self.openArray[-1] = bar.open
        self.closeArray[-1] = bar.close
        self.highArray[-1] = bar.high
        self.lowArray[-1] = bar.low

        self.lips_N[0:self.bufferSize-1] = self.lips_N[1:self.bufferSize]
        self.teeth_N[0:self.bufferSize-1] = self.teeth_N[1:self.bufferSize]
        self.croco_N[0:self.bufferSize-1] = self.croco_N[1:self.bufferSize]

        # 计算xaverage
        if self.bufferCount == 0:
            self.lips_N[-1] = bar.close
            self.teeth_N[-1] = bar.close
            self.croco_N[-1] = bar.close
        else: 
            self.lips_N[-1] = self.lips_N[-2] + 2.0 * (bar.close - self.lips_N[-2])/ (self.CF + 1)
            self.teeth_N[-1] = self.teeth_N[-2] + 2.0 * (bar.close - self.teeth_N[-2])/(self.CM + 1)
            self.croco_N[-1] = self.croco_N[-2] + 2.0 * (bar.close - self.croco_N[-2])/(self.CS + 1) 
        #第一个数值
        self.bufferCount += 1


        if self.bufferCount < self.bufferSize:
            return
    
        # 计算指标数值
        # lips_N = talib.MA(self.closeArray, self.CF)
        # teeth_N = talib.MA(self.closeArray,self.CM)
        # croco_N = talib.MA(self.closeArray,self.CS)

        lips = self.lips_N[0:-self.d_CF]               # python 向前平移 d_CF个单位
        teeth = self.teeth_N[0:-self.d_CM] 
        croco = self.croco_N[0:-self.d_CS]

        zui_value =  0                            # 初始化这个值
        if lips[-1] > teeth[-1] and teeth[-1] > croco[-1]:
            zui_value = 1
        elif lips[-1] < teeth[-1] and teeth[-1] < croco[-1]:
            zui_value = -1
        else:
            zui_value = 0

        self.zui[0:self.bufferSize-1] = self.zui[1:self.bufferSize]
        self.zui[-1] = zui_value

        
        
        cond = 0

        if self.zui[-2] == 1 and self.closeArray[-2] > self.openArray[-2] and self.lowArray[-2] > lips[-2] and self.openArray[-1] > lips[-1]:
            cond = 1
        if self.zui[-2] == -1 and self.closeArray[-2] < self.openArray[-2] and self.highArray[-2] < lips[-2] and self.openArray[-1] < lips[-1]:
            cond = -1

        print bar.datetime, self.lips_N[-1] , self.teeth_N[-1] , self.croco_N[-1] ,lips[-1] , teeth[-1]  , self.zui[-1] , croco[-1] , cond

        if cond > 0:
            if self.pos == 0:
                print bar.datetime , "buy" , bar.open
                vtOrderID = self.buy(bar.open , self.lots)
                self.orderList.append(vtOrderID)
            elif self.pos < 0:
                print bar.datetime , "cover" , bar.open
                vtOrderID = self.cover(bar.open , abs(self.pos))
                self.orderList.append(vtOrderID)
                print bar.datetime , "buy" , bar.open
                vtOrderID = self.buy(bar.open , self.lots)
                self.orderList.append(vtOrderID)
        elif cond < 0:
            if self.pos == 0:
                print bar.datetime , "short" , bar.open
                vtOrderID = self.short(bar.open , self.lots)
                self.orderList.append(vtOrderID)
            elif self.pos > 0:
                print bar.datetime , "sell" , bar.open
                vtOrderID = self.sell(bar.open , abs(self.pos))
                self.orderList.append(vtOrderID)
                print bar.datetime , "short" , bar.open
                vtOrderID = self.short(bar.open , self.lots)
                self.orderList.append(vtOrderID)

        # 判断是否要进行交易
    
        # 当前无仓位，发送OCO开仓委托
        # if self.pos == 0:
        #     self.intraTradeHigh = bar.high
        #     self.intraTradeLow = bar.low            
        #     self.sendOcoOrder(self.kkUp, self.kkDown, self.fixedSize)
    
        # # 持有多头仓位
        # elif self.pos > 0:
        #     self.intraTradeHigh = max(self.intraTradeHigh, bar.high)
        #     self.intraTradeLow = bar.low
            
        #     orderID = self.sell(self.intraTradeHigh*(1-self.trailingPrcnt/100), 
        #                         abs(self.pos), True)
        #     self.orderList.append(orderID)
    
        # # 持有空头仓位
        # elif self.pos < 0:
        #     self.intraTradeHigh = bar.high
        #     self.intraTradeLow = min(self.intraTradeLow, bar.low)
            
        #     orderID = self.cover(self.intraTradeLow*(1+self.trailingPrcnt/100),
        #                        abs(self.pos), True)
        #     self.orderList.append(orderID)
    
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
    from ctaBacktesting import *
    from PyQt4 import QtCore, QtGui
    
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
    engine.setDatabase(MINUTE_DB_NAME, 'IF0000')
    
    # 在引擎中创建策略对象
    d = {}
    engine.initStrategy(KkStrategy, d)
    
    # 开始跑回测
    engine.runBacktesting()
    
    # 显示回测结果
    engine.showBacktestingResult()

if __name__ == '__main__':
    main()