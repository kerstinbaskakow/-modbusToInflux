from influxdb import InfluxDBClient
from pyModbusTCP.client import ModbusClient
import time
import datetime
import pandas as pd
import numpy as np
starttime = time.time()
#timedelta contains programm runtime to be sure to finish before next cronjob starts
timedelta = 120 - (120/100)*17
endtime = starttime+timedelta
timerange = np.arange(starttime,endtime,1)
#define storing time as timebase in influx and grafana
storingtime = datetime.datetime.utcnow()
#initialize list of datapoints that should be stored in influxdb
influxdata=[]
df = pd.DataFrame(columns=['time','registername','value'])
#definition of to be meassured items by register number
measurement_items = {40067:'pv',
                     40071:'hausverbrauch',
                     40082:'soc',
                     40069:'batterieleistung',
                     40073:'netzleistung',
                     40081:'AutarkieUndEigenverbrauch'
                     }
#open influx client
influxclient = InfluxDBClient(host='localhost', port=8086)
influxclient.switch_database('iobroker')

# start modbus client
modbusclient=ModbusClient(host="192.168.2.108",port=502)
modbusclient.open()

#-----define measurement points, each point is a dictionary which -------- 
#----------- is appended to a list of values ---------------------------------
idx = 0
for mytime in timerange:
    time.sleep(1)
    for key,reg in measurement_items.items():
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
            df.loc[idx] = [mytime,'Autarkie',value]
            idx = idx+1
            value = int(bin(regs).split('0b')[1][-8:],2)
            df.loc[idx] = [mytime,'Eigenverbrauch',value]
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
                "value": int(meanvalue),
                        }
            })
#print(influxdata)
#write points to influx database
influxclient.write_points(influxdata, database='iobroker', time_precision='s', batch_size=10000, protocol='json')


modbusclient.close()

#print('Executiontime: ',time.time()-starttime)

