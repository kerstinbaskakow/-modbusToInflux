#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 18 15:17:48 2020

@author: kerstin
"""
class Config:
    DATABASE='iobroker'
    MOD_PORT=502
    MOD_HOST="192.168.2.108"
    INFLUX_PORT=8086
    INFLUX_HOST='localhost'
    PERIOD=120
    
     #definition of to be meassured items by register number
    MEASUREMENT_ITEMS = {40067:'photovoltaikleistung',
                         40071:'hausverbrauchleistung',
                         40082:'soc',
                         40069:'batterieleistung',
                         40073:'netzleistung',
                         40081:'AutarkieUndEigenverbrauch'
                         }
    ENERGIE_ITEMS = ['photovoltaikleistung','hausverbrauchleistung','batterieleistung','netzleistung']