#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 28 13:54:51 2020

@author: kerstin
"""

from influxdb import InfluxDBClient
import datetime
#import numpy as np
from config import Config


#define storing time as timebase in influx and grafana
storingtime = datetime.datetime.utcnow()
#initialize list of datapoints that should be stored in influxdb

dbname = Config.DATABASE
protocol = 'line'
port=Config.INFLUX_PORT
host='localhost'
#open influx client
influxclient = InfluxDBClient(host=host, port=port)
influxclient.switch_database(dbname)

today = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
yesterday = (datetime.datetime.utcnow()-datetime.timedelta(1)).strftime('%Y-%m-%dT%H:%M:%SZ')
#tables
meas_haus = 'modbus.0.holdingRegisters.40071_Hausverbrauch_Leistung'
meas_netz = 'modbus.0.holdingRegisters.40073_Netz_Leistung'
#query and make sum
query_netz= "SELECT sum(value) FROM '{}' WHERE time >= '{}' AND time <= '{}'".format(meas_netz,yesterday,today)
query_haus= "SELECT sum(value) FROM '{}' WHERE time >= '{}' AND time <= '{}'".format(meas_haus,yesterday,today)
netzleistung = influxclient.query(query_netz)
hausverbrauch = influxclient.query(query_haus)
#extract values from resultset
netzleistung_sum = list(netzleistung.get_points(measurement=meas_netz))[0]['sum']
hausleistung_sum = list(netzleistung.get_points(measurement=meas_haus))[0]['sum']
#calculate the autarky value
if netzleistung_sum <= hausleistung_sum:
    autarkiewert = int((1-(netzleistung_sum/hausleistung_sum))*100)
else:
    autarkiewert = 0

#gnerate body for storing in influx
bodyAutarkie = [{
        "measurement": 'autarkie',
        "time": storingtime,
        "fields":
        {
            "value_kb": autarkiewert
        }
    }]
#write to influx
influxclient.write_points(bodyAutarkie, database='iobroker', time_precision='s', batch_size=10000, protocol='json')