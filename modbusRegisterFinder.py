#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct  3 12:15:49 2020

@author: kerstin
"""

from pyModbusTCP.client import ModbusClient

modbusclient=ModbusClient(host="192.168.2.108",port=502)
modbusclient.open()

for x in range(40000,40100,1):
    regs = modbusclient.read_holding_registers(x)[0]
    print(x,': ',regs)

