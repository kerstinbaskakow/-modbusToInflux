# -modbusToInflux

This code reads modbus data from E3DC system to influxdb to be able to view the data in grafana
I recomend not to use this code as I am a beginner :)

Make sure that modbusToInflux.py runs at least twice before energyStatistic.py runs. if not the programm will stop with error

modbusToInflux.py is meant to run each 2 minutes, 
energyStatistic.py is meant to run once per day or once per hour
