#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 14 14:45:48 2020

@author: kerstin
"""
from influxdb import InfluxDBClient
from pyModbusTCP.client import ModbusClient
from config import Config
import time
import datetime
import pandas as pd
import numpy as np

#starttime = time.time()
##timedelta contains programm runtime to be sure to finish before next cronjob starts
#endtime = starttime+Config.PERIOD
#timerange = np.arange(starttime,endtime,1)
#define storing time as timebase in influx and grafana
#storingtime = datetime.datetime.utcnow()
#initialize list of datapoints that should be stored in influxdb
#influxdata=[]
#df = pd.DataFrame(columns=['time','registername','value'])
#open influx client
#influxclient = InfluxDBClient(host='localhost', port=Config.INFLUX_PORT)
#influxclient.switch_database(Config.DATABASE)
#
## start modbus client
#modbusclient=ModbusClient(host=Config.MOD_HOST,port=Config.MOD_PORT)
#modbusclient.open()


class ModbusData():
    def __init__(self,Config=Config,requesttime=1,period=2):
        self.influxclient = InfluxDBClient(host=Config.INFLUX_HOST, port=Config.INFLUX_PORT)
        self.modbusclient=ModbusClient(host=Config.MOD_HOST,port=Config.MOD_PORT)
        self.influxdata = []
        self.df = pd.DataFrame(columns=['time','registername','value'])
        self.storingtime = datetime.datetime.utcnow()
        self.starttime = time.time()
        self.endtime = self.starttime+period
        self.timerange = np.arange(self.starttime,self.endtime,1)
        self.requesttime =requesttime
        
#-----define measurement points, each point is a dictionary which -------- 
#----------- is appended to a list of values ---------------------------------
    def addData(self):
        self.modbusclient.open()
        idx = 0
        for mytime in self.timerange:
            time.sleep(self.requesttime)
            for key,reg in Config.MEASUREMENT_ITEMS.items():
                regs = self.modbusclient.read_holding_registers(key)[0]
                #one register contains two unit8 values, therefore it is converted to 
                #bin and split after 8 bits, the reformated to dec
                if reg=='AutarkieUndEigenverbrauch':
                    #check if the value is available, in case of 0 the string is empty
                    if (bin(regs).split('0b')[1][0:-8]):
                        value=int(bin(regs).split('0b')[1][0:-8],2)
                #if the string is empty write 0 to the database
                    else:
                        value = 0
                    self.df.loc[idx] = [mytime,'autarkie',value]
                    idx = idx+1
                    value = int(bin(regs).split('0b')[1][-8:],2)
                    self.df.loc[idx] = [mytime,'eigenverbrauch',value]
                    idx = idx+1
                #chech signed  ints for leading bit to be 1 or 0, 1 means negativ values
                else:
                    #positive values
                    if regs<32768:
                        value = self.modbusclient.read_holding_registers(key)[0]
                    #negative values (substract 65535 for physical values)
                    else:
                        value = self.modbusclient.read_holding_registers(key)[0]-65535
                        
                    self.df.loc[idx] = [mytime,reg,value]
                    idx = idx+1
            
        for register in self.df.registername.unique():
            meanvalue = self.df[self.df['registername']== register]['value'].mean()
            self.influxdata.append({
                    "measurement": register,
                    "time":self.storingtime,
                    "fields": {
                        "value": int(meanvalue)
                                }
                    })
            #calculate energy:
        for item in Config.ENERGIE_ITEMS:
            energie=self.df[self.df['registername']==item]['value'].sum()  
            energie_wh=energie/3600
            self.influxdata.append({
                    "measurement": item[:-8]+'energie',
                    "time":self.storingtime,
                    "fields": {
                        "value": energie_wh
                                }
                    })
        self.modbusclient.close()
        return self.influxdata
    
    #print(influxdata)
    #write points to influx database
    def writeToInflux(self):
        self.influxclient.switch_database(Config.DATABASE)
        self.influxclient.write_points(self.influxdata, database=Config.DATABASE, time_precision='s', batch_size=10000, protocol='json')
    
    def showInGrafana(self):
        pass
    
    
    
    #print('Executiontime: ',time.time()-starttime)


