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
    query= "SELECT * FROM {}energie WHERE time >= '{}' AND time <= '{}'".format(modul,yesterday,today)
    energy = client.query(query)
    energy_value = list(energy.get_points(measurement='{}energie'.format(modul)))
    df = pd.DataFrame(energy_value)   
    
    bodyDB = [{
        "measurement": '{}statistik'.format(modul),
        "time": storingtime,
        "fields":
        {
            "count": df.describe().loc['count'],
            "mean": df.describe().loc['mean'],
            "std": df.describe().loc['std'],
            "quartile25": df.describe().loc['25%'],
            "quartile50": df.describe().loc['50%'],
            "quartile75": df.describe().loc['75%'],
            "max": df.describe().loc['max'],
            "sum": df['value'].sum(),
            "pos_sum": df[df['value']>0]['value'].sum(),
            "neg_sum": df[df['value']<0]['value'].sum(),
            "abs_sum": df['value'].abs().sum()
            
        }
    }]

    influxclient.write_points(bodyDB, database='iobroker', time_precision='s', batch_size=10000, protocol='json')


for item in Config.ENERGIE_ITEMS:
    calc_energy_statistic(item[:-8],influxclient,storingtime)

