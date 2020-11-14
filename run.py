#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 14 15:10:13 2020

@author: kerstin
"""

from ModbusData import ModbusData

dataMod = ModbusData(period=120)
data = dataMod.addData()
print(data)
dataMod.writeToInflux()