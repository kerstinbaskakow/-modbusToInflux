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
    PERIOD=2
    PERIOD_STREAM=2
    
     #definition of to be meassured items by register number
    MEASUREMENT_ITEMS = {40067:'modbus.0.holdingRegisters.40067_PV_Leistung',
                         40071:'modbus.0.holdingRegisters.40071_Hausverbrauch_Leistung',
                         40082:'soc',
                         40069:'modbus.0.holdingRegisters.40069_Batterie_Leistung',
                         40073:'modbus.0.holdingRegisters.40073_Netz_Leistung',
                         40081:'AutarkieUndEigenverbrauch'
                         }
    ENERGIE_ITEMS = ['modbus.0.holdingRegisters.40067_PV_Leistung',
                     'modbus.0.holdingRegisters.40071_Hausverbrauch_Leistung',
                     'modbus.0.holdingRegisters.40069_Batterie_Leistung',
                     'modbus.0.holdingRegisters.40073_Netz_Leistung']