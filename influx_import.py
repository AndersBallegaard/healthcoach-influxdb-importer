#!/usr/bin/python3
import json
from datetime import datetime
import lnetatmo
from influxdb import InfluxDBClient
import requests

USERNAME = None
PASSWORD = None
CLIENTID = None
CLIENTSECRET = None
HOMECOACHES = []
INFLUXDBSERVER = None

with open("settings.json") as f:
    j = json.loads(f.read())
    USERNAME = j["username"]
    PASSWORD = j["password"]
    CLIENTID = j["clientID"]
    CLIENTSECRET = j["clientSecret"]
    HOMECOACHES = j["homeCoachDevices"]
    INFLUXDBSERVER = j["influxDB_server"]

authorization = lnetatmo.ClientAuth(
        clientId=CLIENTID,
        clientSecret=CLIENTSECRET,
        username=USERNAME,
        password=PASSWORD,
        scope='read_homecoach'
        )

header = {
    "Authorization": f"Bearer {authorization.accessToken}"
}

client = InfluxDBClient(host=INFLUXDBSERVER)
if {'name': 'netatmo'} not in client.get_list_database():
    client.create_database('netatmo')

for homecoach in HOMECOACHES:
    data_resp = requests.get(f"https://api.netatmo.com/api/gethomecoachsdata?device_id={homecoach}", headers=header)
    dataset = data_resp.json()["body"]["devices"]
    for data in dataset:
        name = data["station_name"]
        dashboard = data["dashboard_data"]

        # Create point with some bullshit convertion because influx won't convert an int to float
        point = {
            "measurement": "HomeCoach",
            "tags": {
                "name": name
            },
            "time": datetime.now().utcnow(),
            "fields": {
                "AbsolutePressure": float(dashboard["AbsolutePressure"]),
                "CO2": int(dashboard["CO2"]),
                "Humidity": int(dashboard["Humidity"]),
                "Noise": int(dashboard["Noise"]),
                "Pressure": float(dashboard["Pressure"]),
                "Temperature": float(dashboard["Temperature"]),
                "date_max_temp": int(dashboard["date_max_temp"]),
                "date_min_temp": int(dashboard["date_min_temp"]),
                "health_idx": int(dashboard["health_idx"]),
                "max_temp": float(dashboard["max_temp"]),
                "min_temp": float(dashboard["min_temp"]),
                
            }
        }
        client.write_points([point], database="netatmo")