import serial
import csv
from datetime import datetime
import time

PORT = 'COM4'   # 🔧 change if needed
BAUD = 9600

def connect_serial():
    while True:
        try:
            ser = serial.Serial(PORT, BAUD, timeout=1)
            print(f"✅ Connected to {PORT}")
            return ser
        except Exception as e:
            print(f"❌ Port busy or not available: {e}")
            print("👉 Close Arduino Serial Monitor / check port...")
            time.sleep(3)

ser = connect_serial()

with open('sensor_data.csv', 'w', newline='') as f:

    writer = csv.writer(f)
    writer.writerow(["time", "temperature", "current", "status"])

    print("📊 Logging started... Press CTRL+C to stop")

    while True:
        try:
            line = ser.readline().decode(errors='ignore').strip()

            if not line:
                continue

            values = line.split(",")

            # Expecting: temp,current,status
            if len(values) != 3:
                continue

            temp, current, status = values

            time_now = datetime.now().strftime("%H:%M:%S")

            writer.writerow([time_now, temp, current, status])

            print(f"{time_now} | Temp: {temp} | Current: {current} | Status: {status}")

        except KeyboardInterrupt:
            print("\n🛑 Logging stopped by user")
            break

        except Exception as e:
            print("⚠️ Error:", e)