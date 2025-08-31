# database/influx_client.py

from influxdb_client import InfluxDBClient, Point, WriteOptions
from influxdb_client.client.write_api import SYNCHRONOUS
import os

class InfluxClient:
    def __init__(self):
        self.url = os.getenv('INFLUXDB_URL', "http://localhost:8086")
        self.token = os.getenv('INFLUXDB_TOKEN', "<your-token>")
        self.org = os.getenv('INFLUXDB_ORG', "<your-org>")
        self.bucket = os.getenv('INFLUXDB_BUCKET', "<your-bucket>")
        self.client = InfluxDBClient(url=self.url, token=self.token, org=self.org)
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
        self.query_api = self.client.query_api()

    def write_measurement(self, measurement, tags: dict, fields: dict, timestamp=None):
        """
        Write a single measurement to influxdb.
        """
        point = Point(measurement)
        for k, v in (tags or {}).items():
            point = point.tag(k, v)
        for k, v in (fields or {}).items():
            point = point.field(k, v)
        if timestamp is not None:
            point = point.time(timestamp)
        self.write_api.write(bucket=self.bucket, org=self.org, record=point)

    def write_batch(self, points):
        """
        points: list of influxdb_client.Point
        """
        self.write_api.write(bucket=self.bucket, org=self.org, record=points)

    def query(self, flux_query: str):
        """
        Run an InfluxDB Flux query and return the result.
        """
        return self.query_api.query(flux_query, org=self.org)

    def close(self):
        self.client.close()

# Singleton instance for easy import
influx_client = InfluxClient()

# Example usage:
# influx_client.write_measurement(
#     "threats",
#     tags={"location": "Mumbai"},
#     fields={"tide_level": 3.7, "wind_speed": 40, "severity": 0.8}
# )
