#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 18 10:51:44 2020

@author: kerstin
"""

from influxdb import InfluxDBClient
import datetime
import pandas as pd
#import numpy as np
from config import Config


#define storing time as timebase in influx and grafana
storingtime = datetime.datetime.utcnow()
#initialize list of datapoints that should be stored in influxdb
influxdata=[]

dbname = Config.DATABASE
protocol = 'line'
port=Config.INFLUX_PORT
host='localhost'
#open influx client
influxclient = InfluxDBClient(host=host, port=port)
influxclient.switch_database(dbname)

def calc_energy_statistic(modul,client,storingtime):
    today = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    yesterday = (datetime.datetime.utcnow()-datetime.timedelta(1)).strftime('%Y-%m-%dT%H:%M:%SZ')
    query= 'SELECT * FROM "{}" '.format(modul)+"WHERE time >= '{}' AND time <= '{}'".format(yesterday,today)

    energy = client.query(query)
    energy_value = list(energy.get_points(measurement='{}'.format(modul)))
    df = pd.DataFrame(energy_value)   
    bodyDB = [{
        "measurement": '{}_statistik'.format(modul.rsplit("_")[1]),
        "time": storingtime,
        "fields":
        {
            "gespeicherteWerteProTag": df.describe().loc['count'],
            "LeistungMittelwert": df.describe().loc['mean'],
            "LeistungStandardabweichung": df.describe().loc['std'],
            "LeistungQuartile25": df.describe().loc['25%'],
            "LeistungQuartile50": df.describe().loc['50%'],
            "LeistungQuartile75": df.describe().loc['75%'],
            "LeistungMaxProTag": df.describe().loc['max'],
            "LeistungMinProTag": df.describe().loc['min'],
            "Energie_pos": df[df['value']>0]['value'].sum(),
            "Energie_neg": df[df['value']<0]['value'].sum(),
            "EnergiedurchsatzProTag": df['value'].abs().sum()
            
        }
    }]
    #print(bodyDB)
    influxclient.write_points(bodyDB, database='iobroker', time_precision='s', batch_size=10000, protocol='json')
    return df

autark_dict=dict()
for item in Config.ENERGIE_ITEMS:
    df = calc_energy_statistic(item,influxclient,storingtime)
    autark_dict[item] = df[df['value']>0]['value'].sum()

#
if autark_dict['modbus.0.holdingRegisters.40073_Netz_Leistung'] <= autark_dict['modbus.0.holdingRegisters.40071_Hausverbrauch_Leistung']:
    autarkiewert = int((1-(autark_dict['modbus.0.holdingRegisters.40073_Netz_Leistung']/autark_dict['modbus.0.holdingRegisters.40071_Hausverbrauch_Leistung']))*100)
else:
    autarkiewert = 0

bodyAutarkie = [{
        "measurement": 'autarkie',
        "time": storingtime,
        "fields":
        {
            "value_kb": autarkiewert
        }
    }]
influxclient.write_points(bodyAutarkie, database='iobroker', time_precision='s', batch_size=10000, protocol='json')

