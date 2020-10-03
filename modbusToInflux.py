from influxdb import InfluxDBClient
from pyModbusTCP.client import ModbusClient
import datetime
import time
starttime = time.time()

#open influx client
influxclient = InfluxDBClient(host='localhost', port=8086)
influxclient.switch_database('iobroker')


modbusclient=ModbusClient(host="192.168.2.108",port=502)
modbusclient.open()

measurement_items = [{'pv':40067},{'hausverbrauch':40071},{'soc':40082}]

#while True:
mytime = datetime.datetime.utcnow()
influxdata=[]
for item in measurement_items:
    for key,reg in item.items():
        influxdata.append({
        "measurement": key,
        "time":mytime,
        "fields": {
            "value": modbusclient.read_holding_registers(reg)[0],
                    }
    })

influxclient.write_points(influxdata, database='iobroker', time_precision='ms', batch_size=10000, protocol='json')

#    time.sleep(60.0 - ((time.time() - starttime) % 60.0))

modbusclient.close()

