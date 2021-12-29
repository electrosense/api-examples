# !/usr/bin/env python
#  Copyright (C) IMDEA Networks Institute 2016
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
#  Author : Alessio Scalingi <alessio [dot] scalingi [at] imdea [dot] org)

import json
import requests
from requests.auth import HTTPBasicAuth
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from geopy.geocoders import Nominatim
def plot_sensors_by_countries(df):
    df2 = df['country'].value_counts().reset_index()
    df2.columns = ['country', 'count']
    df2 = df2.sort_values(by='count')
    df2['count'].sum()
    df2
    # Declaring the figure or the plot (y, x) or (width, height)
    plt.figure(figsize=[14, 10])
    # Passing the parameters to the bar function, this is the main function which creates the bar plot
    # For creating the horizontal make sure that you append 'h' to the bar function name
    df2.sort_values(by='count', ascending=True)
    N=len(df2)
    cmap = plt.cm.tab10
    colors = cmap(np.arange(len(df2)) % cmap.N)
    plt.barh(df2['country'].values, df2['count'].values,color=colors, edgecolor='black')

    # Creating the legend of the bars in the plot
    plt.legend()
    # Namimg the x and y axis
    plt.xlabel('Number of sensor',fontsize=30)
    #plt.ylabel('Countries',fontsize=30)
    # Giving the tilte for the plot
    plt.title("Online Sensors by Countries", fontsize=30)
    plt.rc('ytick',labelsize=20)
    plt.rc('xtick',labelsize=20)
    # Saving the plot as a 'png'
    #plt.savefig('2BarPlot.png')
    # Displaying the bar plot

    plt.text(10.2, 0.8, "Total: %d"%df2['count'].sum(), size=20,
             ha="center", va="center",
             bbox=dict(facecolor='grey',alpha=0.1,boxstyle="round",edgecolor='black')

            )


    plt.show()
def get_city(row):
    try:
        lat = row['lat']
        lon = row['lon']
        coord = str(lon)+", "+str(lat)
        geolocator = Nominatim(user_agent="Electrosense")
        location = geolocator.reverse(coord)
        addr= location.address
    except Exception as error:
        print(error)
        return "None"
        pass
    else:
        return addr.split(",")[1].strip()

# Electrosense API Credentials  (add HERE your credentials)
username = 'scalessio'  # options.username
password = 'zuwhaw-sefda5-Fukfat'  # options.password

# Electrosense API
MAIN_URI = 'https://electrosense.org/api'
SENSOR_LIST = MAIN_URI + '/sensor/list/'

r = requests.get(SENSOR_LIST, auth=HTTPBasicAuth(username, password))

if r.status_code != 200:
    print(r.content)
    exit(-1)

slist_json = json.loads(r.content)
lista_sensing =  []
for i, sensor in enumerate(slist_json):
    if sensor['sensing'] is True:
        lista_sensing.append(i)

df = pd.DataFrame()
s = pd.Series(['name','latitude','longitude','country'])
for pos in lista_sensing:
    df = df.append(s.map({'name': slist_json[pos]['name'], 'latitude': slist_json[pos]['position']['longitude'],
       'longitude': slist_json[pos]['position']['latitude'],'country': slist_json[pos]['country']}), ignore_index=True)


df.columns = ['Sensor Name','lat','lon','country']
df["City"] = df.apply(get_city, axis=1)


country_df = df[df.country == 'Italy'].reset_index()
country_df['City'] = country_df['City'].apply(lambda x : x.lstrip())
country_df[country_df['City'] == 'Comunidad de Madrid']
country_df = country_df.drop(['index'], axis=1)
country_df.columns = ['Sensor Name', 'lon', 'lat', 'country', 'City']
dic = country_df[['Sensor Name', 'lat', 'lon']].to_dict()

with open('resources/data.json', 'w') as fp:
    json.dump(dic, fp)