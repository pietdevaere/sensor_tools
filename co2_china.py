import sys
import serial
import serial.tools.list_ports
import time

import sensing_tools
 
class CO2Sensor:
    def __init__(self, serial_port_name = None):
        if not serial_port_name:
            ports = serial.tools.list_ports.comports()

            if len(ports) == 0:
                print("No serial ports found, goodbye.")
                sys.exit(1)
            
            serial_port = None
            
            print("Found the following serial ports:")
            for port in ports:
                print("\t" + str(port))
                if port.product.startswith("CP2104"):
                    serial_port = port

            if serial_port is None:
                print("No good serial port found, goodbye")
                sys.exit(2)


            print("Using port:", serial_port.device)
            
            self.port_info = serial_port
            self.serial = serial.Serial(serial_port.device, 9600)

    def read(self):
        self.serial.write(bytes([0xFF, 0x01, 0x86, 0x00, 0x00, 0x00, 0x00, 0x00, 0x79]))
        response = self.serial.read(9)
        reading = int(response[2])*256 + int(response[3])

        return reading     

if __name__ == "__main__":
    sensor = CO2Sensor()
    reporter = sensing_tools.InfluxReporter("secrets.json")

    while True:

        start = time.time()

        co2_concentration = sensor.read()
        print("CO2 Concentration: " + str(co2_concentration) + " ppm")
       	reporter.report("co2", "MH-Z19B", "CAB F81", co2_concentration) 
        
        wait = max(0, start + 1 - time.time())
        time.sleep(wait)
