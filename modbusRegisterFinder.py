#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct  3 12:15:49 2020

@author: kerstin
"""

from pyModbusTCP.client import ModbusClient
import pandas as pd

modbusclient=ModbusClient(host="192.168.2.108",port=502)
modbusclient.open()

measurement_items = {40067:'pv',
                     40071:'hausverbrauch',
                     40082:'soc',
                     40069:'Batterieleistung',
                     40073:'Netz',
                     40081:'AutarkieUndEigenverbrauch'}
name = None

print('Batterie: positiv: Laden, Negativ:entladen')
print('Netz: positiv: Bezug, Negativ: Einspeisen')
df = pd.DataFrame(columns=['name','rawValue','physValue','rawBin'])

registerListe = []
for x in range(40000,40100,1):

    regs = modbusclient.read_holding_registers(x)[0]
    print(x,regs)
    registerListe.append((x,regs))
    rawBin= bin(regs).split('0b')[1]
    name = measurement_items.get(x)
    if name=='AutarkieUndEigenverbrauch':
        autarkie=int(bin(regs).split('0b')[1][0:-8],2)
        eigenverbrauch = int(bin(regs).split('0b')[1][-8:],2)
        df.loc[x+20000] = ['Autarkie',regs,autarkie,rawBin]
        df.loc[x] = ['Eigenverbrauch',regs,eigenverbrauch,rawBin]
    elif name:
        if regs<32768:
            df.loc[x] = [name,regs,regs,rawBin]
        else:
            df.loc[x] = [name,regs,regs-65535,rawBin]
    #else:
    #    df.loc[x] = [name,regs,None,rawBin]
#df.to_csv('modbusRegisterList.csv')
df_register = pd.DataFrame(registerListe,columns=['register','rawValue'])           
print(df_register)
df_register.to_csv('modbusUnknownRegisterList.csv')

modbusclient.close()

