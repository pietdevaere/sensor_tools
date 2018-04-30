import json
import time

from influxdb import InfluxDBClient

def read_secrets(secret_file_path):
    with open(secret_file_path) as secret_file:
        return json.loads(secret_file.read())

class InfluxReporter:
    def __init__(self, secret_file_path):
        self.config = read_secrets(secret_file_path)['influx']

        self.client = InfluxDBClient(   self.config['host'],
                                        self.config['port'],
                                        self.config['user'],
                                        self.config['password'],
                                        self.config['database'],
                                        ssl = self.config['ssl'],
                                        verify_ssl = True)

        self.buffer = list()

    def add_measurement(self, measurement, sensor, location, value):
        buffer_entry = { "measurement": measurement,
                        "tags": {
                            "sensor" :   sensor,
                            "location" : location,
                            },
                        "fields" : {
                            "value": value,
                            },
                        "time" : time.time()
                        }
        self.buffer.append(buffer_entry)

    def transmit(self):
        self.client.write_points(json_body)


    def report(self, measurement, sensor, location, value):
        self.add_measurement(measurement, sensor, location, value)
        self.transmit()


if __name__ == "__main__":
    reporter = InfluxReporter('secrets.json')
