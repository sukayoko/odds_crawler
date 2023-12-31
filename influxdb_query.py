import influxdb_client, os, time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

# token = os.environ.get("INFLUXDB_TOKEN")
token = "BpuYs_ip6nKxvL2fcIBYqp8hxaz4x_94TgmKNeEjHwfq1SoIGPj87_IxyY47JjL8s558PyVO6vkAuVqBGTTEOQ=="
org = "organization"
url = "http://192.168.1.118:8086"

client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)

bucket="bkt1"

query_api = client.query_api()

query = """from(bucket: "bkt1")
 |> range(start: -10m)
 |> filter(fn: (r) => r._measurement == "measurement1")"""
tables = query_api.query(query, org="organization")

for table in tables:
  for record in table.records:
    print(record)

print("---------------------")

query = """from(bucket: "bkt1")
  |> range(start: -10m)
  |> filter(fn: (r) => r._measurement == "measurement1")
  |> mean()"""
tables = query_api.query(query, org="organization")

for table in tables:
    for record in table.records:
        print(record)