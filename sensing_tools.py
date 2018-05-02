import sys
import json
import datetime

import influxdb.exceptions
import requests.exceptions

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
                                        verify_ssl = True,
                                        timeout = 1,
                                        retries = 1)

        self.buffer = list()

    def add_measurement(self, measurement, sensor, location, value):
        utc_now = datetime.datetime.now(datetime.timezone.utc)
        now = utc_now.astimezone()
        buffer_entry = { "measurement": measurement,
                        "tags": {
                            "sensor" :   sensor,
                            "location" : location,
                            },
                        "fields" : {
                            "value": value,
                            },
                        "time" : now.isoformat()
                        }
        print(buffer_entry)
        self.buffer.append(buffer_entry)

    def transmit_buffer(self):
        try:
            self.client.write_points(self.buffer)
        except requests.exceptions.RequestException:
            print("Request exception when contacting influxDB")
        except Exception as ex:
            template = "An unexpected exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print(message)
            sys.exit(1)
        else:
            self.buffer = list()

    def report(self, measurement, sensor, location, value):
        self.add_measurement(measurement, sensor, location, value)
        self.transmit_buffer()


if __name__ == "__main__":
    reporter = InfluxReporter('secrets.json')
