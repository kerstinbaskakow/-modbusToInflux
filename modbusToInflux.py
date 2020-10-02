from influxdb import InfluxDBClient
from pyModbusTCP.client import ModbusClient
import datetime
import time
starttime = time.time()


influxclient = InfluxDBClient(host='localhost', port=8086)
influxclient.switch_database('iobroker')


modbusclient=ModbusClient(host="192.168.2.108",port=502)
modbusclient.open()

while True:
    pv = modbusclient.read_holding_registers(40067)[0]
    hausverbrauch = modbusclient.read_holding_registers(40071)[0]
    soc = modbusclient.read_holding_registers(40082)[0]
    mytime = datetime.datetime.utcnow()
    print("pv: ",pv)
    print("hausverbrauch: ",hausverbrauch)
    print("soc: ",soc)
    print("time: ",mytime)
    influxdata_pv=[
    {
        "measurement": "pvLeistung",
        "time":mytime,
        "fields": {
            "value": pv,
                    }
    }]
    influxdata_haus=[
    {
        "measurement": "hausverbrauch",
        "time":mytime,
        "fields": {
            "value":hausverbrauch,
                    }
    }]
    influxdata_batterie=[
    {
        "measurement": "soc",
        "time":mytime,
        "fields": {
            "value":soc,
                    }
    }]

    
    
    
    influxclient.write_points(influxdata_pv, database='iobroker', time_precision='ms', batch_size=10000, protocol='json')
    influxclient.write_points(influxdata_haus, database='iobroker', time_precision='ms', batch_size=10000, protocol='json')
    influxclient.write_points(influxdata_batterie, database='iobroker', time_precision='ms', batch_size=10000, protocol='json')

    #print(influxclient.query('SELECT * FROM "MyPVAnlageData"'))
    time.sleep(60.0 - ((time.time() - starttime) % 60.0))

modbusclient.close()

