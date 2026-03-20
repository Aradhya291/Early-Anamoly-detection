import serial
import csv
from datetime import datetime

# change port according to your system
ser = serial.Serial('COM3',9600)

with open('sensor_data.csv','w',newline='') as f:

    writer = csv.writer(f)
    writer.writerow(["time","temperature","gas"])

    print("Logging started...")

    while True:

        line = ser.readline().decode().strip()

        temp,gas = line.split(",")

        time = datetime.now().strftime("%H:%M:%S")

        writer.writerow([time,temp,gas])

        print(time,temp,gas)