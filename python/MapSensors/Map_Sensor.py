# !/usr/bin/env python
#  Copyright (C) IMDEA Networks Institute 2022
#
# This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with this program.  If not,
# see http://www.gnu.org/licenses/.
#
#  Author : Alessio Scalingi <alessio [dot] scalingi [at] imdea [dot] org

import json
import requests
from requests.auth import HTTPBasicAuth
import pandas as pd
from geopy.geocoders import Nominatim

def get_city(row):
    try:
        lat = row['lat']
        lon = row['lon']
        coord = str(lon) + ", " + str(lat)
        geolocator = Nominatim(user_agent="Electrosense")
        location = geolocator.reverse(coord)
        addr = location.address
    except Exception as error:
        print(error)
        return "None"
        pass
    else:
        return addr.split(",")[1].strip()

# Electrosense API Credentials
username = str(input("Enter Your ElectroSense Username: "))
password = str(input("Enter Password: "))

# Electrosense API
MAIN_URI = 'https://electrosense.org/api'
SENSOR_LIST = MAIN_URI + '/sensor/list/'

r = requests.get(SENSOR_LIST, auth=HTTPBasicAuth(username, password))

if r.status_code != 200:
    print(r.content)
    exit(-1)

slist_json = json.loads(r.content)
lista_sensing = []
for i, sensor in enumerate(slist_json):
    if sensor['sensing'] is True:
        lista_sensing.append(i)

df = pd.DataFrame()
s = pd.Series(['name', 'latitude', 'longitude', 'country'])
for pos in lista_sensing:
    df = df.append(s.map({'name': slist_json[pos]['name'], 'latitude': slist_json[pos]['position']['longitude'],
                          'longitude': slist_json[pos]['position']['latitude'], 'country': slist_json[pos]['country']}),
                   ignore_index=True)

df.columns = ['Sensor Name', 'lat', 'lon', 'country']
df["City"] = df.apply(get_city, axis=1)

print(df['country'].value_counts().index.to_list())
print("Type Country:  \n")
Country = str(input("Enter Country "))  # 28

country_df = df[df.country == Country].reset_index()
country_df['City'] = country_df['City'].apply(lambda x: x.lstrip())
country_df = country_df.drop(['index'], axis=1)
country_df.columns = ['Sensor Name', 'lon', 'lat', 'country', 'City']
dic = country_df[['Sensor Name', 'lat', 'lon']].to_dict()
with open('resources/data.json', 'w') as fp:
    json.dump(dic, fp)
