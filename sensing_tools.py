import json
import datetime

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
                        "time" : datetime.datetime.now().isoformat()
                        }
        self.buffer.append(buffer_entry)

    def transmit_buffer(self):
        self.client.write_points(self.buffer)
        self.buffer = list()


    def report(self, measurement, sensor, location, value):
        self.add_measurement(measurement, sensor, location, value)
        self.transmit_buffer()


if __name__ == "__main__":
    reporter = InfluxReporter('secrets.json')
