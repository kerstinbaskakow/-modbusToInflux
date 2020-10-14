from influxdb import InfluxDBClient
from pyModbusTCP.client import ModbusClient
import datetime
import time
starttime = time.time()

#open influx client
influxclient = InfluxDBClient(host='localhost', port=8086)
influxclient.switch_database('iobroker')

# start modbus client
modbusclient=ModbusClient(host="192.168.2.108",port=502)
modbusclient.open()

#definition of to be meassured items by register number
measurement_items = {40067:'pv',
                     40071:'hausverbrauch',
                     40082:'soc',
                     40069:'batterieleistung',
                     40073:'netzleistung',
                     40081:'AutarkieUndEigenverbrauch'
                     }
#define storing time as timebase in influx and grafana
mytime = datetime.datetime.utcnow()

#initialize list of datapoints that should be stored in influxdb
influxdata=[]
#alive counter integration to check why modbus values are not available
alivecounter = influxclient.query('SELECT value FROM alivecounter order by time desc limit 1')
if alivecounter:
    alivecounter_value = list(alivecounter.get_points(measurement='alivecounter'))[0]['value']
    if alivecounter_value > 14:
        alivecounter_value = 0
    else:
        alivecounter_value=alivecounter_value +1
else:
    alivecounter_value = 0



influxdata.append({
        "measurement": "alivecounter",
        "time":mytime,
        "fields": {
                "value": alivecounter_value,
                }
        })
#define measurement points, each point is a dictionary appended to a list of 
#points

for key,reg in measurement_items.items():
    print(reg,key)
    regs = modbusclient.read_holding_registers(key)[0]
    print(regs)
    #one register contains two unit8 values, therefore it is converted to 
    #bin and split after 8 bits, the reformated to dec
    if reg=='AutarkieUndEigenverbrauch':
        print(reg,':')
        print('raw value: ',regs)
        print('binvalue:',bin(regs))
        print(bin(regs).split('0b')[1])
        print('binvalue aftersplit:',bin(regs).split('0b')[1][0:-8])
        if (bin(regs).split('0b')[1][0:-8]):
            autarkie=int(bin(regs).split('0b')[1][0:-8],2)
            print('autarkie:',autarkie)
            influxdata.append({
                "measurement": "autarkie",
                "time":mytime,
                "fields": {
                    "value": autarkie,
                            }
                })
        else:
                        
            influxdata.append({
                "measurement": "autarkie",
                "time":mytime,
                "fields": {
                    "value": 0,
                            }
                })
        eigenverbrauch = int(bin(regs).split('0b')[1][-8:],2)
        influxdata.append({
            "measurement": "eigenverbrauch",
            "time":mytime,
            "fields": {
                "value": eigenverbrauch,
                        }
            })
    #chech signed  ints for leading bit to be 1 or 0, 1 means negativ values
    elif reg:
        print(reg,'elif')
        #positive values
        if regs<32768:
            influxdata.append({
            "measurement": reg,
            "time":mytime,
            "fields": {
                "value": modbusclient.read_holding_registers(key)[0],
                        }
            })
        #negative values (substract 65535 for physical values)
        else:
            influxdata.append({
            "measurement": reg,
            "time":mytime,
            "fields": {
                "value": modbusclient.read_holding_registers(key)[0]-65535,
                        }
            })
    

#print(influxdata)

#write points to influx database
influxclient.write_points(influxdata, database='iobroker', time_precision='ms', batch_size=10000, protocol='json')


modbusclient.close()

