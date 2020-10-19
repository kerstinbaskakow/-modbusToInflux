from influxdb import InfluxDBClient
from pyModbusTCP.client import ModbusClient
from config import Config
import time
import datetime
import pandas as pd
import numpy as np
starttime = time.time()
#timedelta contains programm runtime to be sure to finish before next cronjob starts
endtime = starttime+Config.PERIOD
timerange = np.arange(starttime,endtime,1)
#define storing time as timebase in influx and grafana
storingtime = datetime.datetime.utcnow()
#initialize list of datapoints that should be stored in influxdb
influxdata=[]
df = pd.DataFrame(columns=['time','registername','value'])
#open influx client
influxclient = InfluxDBClient(host='localhost', port=Config.INFLUX_PORT)
influxclient.switch_database(Config.DATABASE)

# start modbus client
modbusclient=ModbusClient(host=Config.MOD_HOST,port=Config.MOD_PORT)
modbusclient.open()

#-----define measurement points, each point is a dictionary which -------- 
#----------- is appended to a list of values ---------------------------------
idx = 0
requesttime =1
for mytime in timerange:
    time.sleep(requesttime)
    for key,reg in Config.MEASUREMENT_ITEMS.items():
        regs = modbusclient.read_holding_registers(key)[0]
        #one register contains two unit8 values, therefore it is converted to 
        #bin and split after 8 bits, the reformated to dec
        if reg=='AutarkieUndEigenverbrauch':
            #check if the value is available, in case of 0 the string is empty
            if (bin(regs).split('0b')[1][0:-8]):
                value=int(bin(regs).split('0b')[1][0:-8],2)
        #if the string is empty write 0 to the database
            else:
                value = 0
            df.loc[idx] = [mytime,'autarkie',value]
            idx = idx+1
            value = int(bin(regs).split('0b')[1][-8:],2)
            df.loc[idx] = [mytime,'eigenverbrauch',value]
            idx = idx+1
        #chech signed  ints for leading bit to be 1 or 0, 1 means negativ values
        else:
            #positive values
            if regs<32768:
                value = modbusclient.read_holding_registers(key)[0]
            #negative values (substract 65535 for physical values)
            else:
                value = modbusclient.read_holding_registers(key)[0]-65535
                
            df.loc[idx] = [mytime,reg,value]
            idx = idx+1
    
for register in df.registername.unique():
    meanvalue = df[df['registername']== register]['value'].mean()
    influxdata.append({
            "measurement": register,
            "time":storingtime,
            "fields": {
                "value": int(meanvalue)
                        }
            })
#calculate energy:
for item in Config.ENERGIE_ITEMS:
    energie=df[df['registername']==item]['value'].sum()  
    energie_wh=energie/3600
    influxdata.append({
            "measurement": item[:-8]+'energie',
            "time":storingtime,
            "fields": {
                "value": energie_wh
                        }
            })  

#print(influxdata)
#write points to influx database
influxclient.write_points(influxdata, database='iobroker', time_precision='s', batch_size=10000, protocol='json')


modbusclient.close()

#print('Executiontime: ',time.time()-starttime)

