from flask import Flask
import json
from config import Config
from pyModbusTCP.client import ModbusClient

class ModbusData():
    def __init__(self,Config=Config):
        self.modbusclient=ModbusClient(host=Config.MOD_HOST,port=Config.MOD_PORT)
        self.data = []
        self.MEASUREMENT_ITEMS = {40067:'photovoltaikleistung',
                         40071:'hausverbrauchleistung',
                         40082:'soc',
                         40069:'batterieleistung',
                         40073:'netzleistung'
                         }
#-----define measurement points, each point is a dictionary which -------- 
#----------- is appended to a list of values ---------------------------------
    def addData(self):
        self.modbusclient.open()      
        for key,reg in self.MEASUREMENT_ITEMS.items():
            regs = self.modbusclient.read_holding_registers(key)[0]
            #chech signed  ints for leading bit to be 1 or 0, 1 means negativ values
            #positive values
            if regs<32768:
                value = self.modbusclient.read_holding_registers(key)[0]
            #negative values (substract 65535 for physical values)
            else:
                value = self.modbusclient.read_holding_registers(key)[0]-65535
            self.data.append({
                    reg:value
                    })
            

        self.modbusclient.close()
        return self.data

app = Flask(__name__)
dataMod = ModbusData()
@app.route('/search', methods=['POST','GET'])
def search():
    data = dataMod.addData()
    return json.dumps(data)


@app.route('/', methods=['POST','GET'])
def show():
    #dataMod = ModbusData()
    data = dataMod.addData()
    return json.dumps(data)

if __name__ == '__main__':
    app.run(host='localhost', port=8085)
