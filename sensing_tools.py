import json

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

    def report(self, measurement, sensor, location, value):
        json_body = [ { "measurement": measurement,
                        "tags": {
                            "sensor" :   sensor,
                            "location" : location,
                            },
                        "fields" : {
                            "value": value,
                            },
                        } ]
        self.client.write_points(json_body)




if __name__ == "__main__":
    reporter = InfluxReporter('secrets.json')
