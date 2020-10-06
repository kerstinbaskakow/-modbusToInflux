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

#define measurement points, each point is a dictionary appended to a list of 
#points
influxdata=[]
for key,reg in measurement_items.items():
    regs = modbusclient.read_holding_registers(key)[0]
    #one register contains two unit8 values, therefore it is converted to 
    #bin and split after 8 bits, the reformated to dec
    if reg=='AutarkieUndEigenverbrauch':
        autarkie=int(bin(regs).split('0b')[1][0:-8],2)
        influxdata.append({
            "measurement": "autarkie",
            "time":mytime,
            "fields": {
                "value": autarkie,
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
    

print(influxdata)

#write points to influx database
influxclient.write_points(influxdata, database='iobroker', time_precision='ms', batch_size=10000, protocol='json')


modbusclient.close()

