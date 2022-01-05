#!/usr/bin/env python
#
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
#  Author : Alessio Scalingi <alessio [dot] scalingi [at] imdea [dot] org:
#

from urllib.parse import urlencode
import requests
import json
import datetime
import time
from requests.auth import HTTPBasicAuth
from collections import OrderedDict
import calendar
from matplotlib import cm
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

def get_spectrum_data(sensor_id, timeBegin, timeEnd, freq_min, freq_max, aggTime, aggFreq):
    params = OrderedDict([('sensor', sensor_id),
                          ('timeBegin', timeBegin),
                          ('timeEnd', timeEnd),
                          ('freqMin', freq_min),
                          ('freqMax', freq_max),
                          ('aggFreq', aggFreq),
                          ('aggTime', aggTime),
                          ('aggFun', 'AVG')])

    r = requests.get(SENSOR_AGGREGATED, auth=HTTPBasicAuth(username, password), params=urlencode(params))

    print(r.url)
    print(r.status_code)
    print(r.content)

    if r.status_code == 200:
        return json.loads(r.content)
    else:
        print("Response: %d" % (r.status_code))
        return None

# Electrosense API Credentials
username = str(input("Enter Your ElectroSense Username: "))
password = str(input("Enter Password: "))

# Electrosense API
MAIN_URI ='https://electrosense.org/api'
SENSOR_LIST = MAIN_URI + '/sensor/list/'
SENSOR_AGGREGATED = MAIN_URI + "/spectrum/aggregated"

r = requests.get(SENSOR_LIST, auth=HTTPBasicAuth(username, password))
slist_json = json.loads(r.content)
sensing_sensors_list = []
for sensor in slist_json:
    if (sensor['sensing']):
        sensing_sensors_list.append(sensor)

count_active_sensor = 0
for sensor in sensing_sensors_list:
    sname,sserial,scountry = str(sensor['name']),sensor['serial'],sensor['country']
    print("Pos: ",count_active_sensor, sname, sserial)
    count_active_sensor += 1


print(" \n Select the sensor to plot the Spectrum Waterfall \n")
sensor1 = int(input("Enter sensor position  "))  # 28

sensor_id_A = sensing_sensors_list[sensor1]['serial']
sensor_name_A = sensing_sensors_list[sensor1]['name']
sensor_country_A = sensing_sensors_list[sensor1]['country']

check_day = True
now = datetime.datetime.now()
while check_day:
    day = input("Enter the day [dd]  ")  # 28
    month = input("Enter the month [mm]  ")
    year = input("Enter the year [yyyy]  ")

    if int(day) < 31 and int(month) <= 12 and int(year) <= now.year:
        check_day = False
    elif int(month) == 2 and int(day) > 28: # We dont handle the case if feb has 29 day
        print("Please insert a true date")
    else:
        print("Please insert a true date")


timestr = month+" "+day+" "+"10:00:00 "+year
calendar.timegm(time.strptime(timestr, "%m %d %H:%M:%S %Y"))


timestr = month+" "+day+" "+"10:00:00 "+year
calendar.timegm(time.strptime(timestr, "%m %d %H:%M:%S %Y"))


# epoch_time = 1599300000
epoch_time = calendar.timegm(time.strptime(timestr, "%m %d %H:%M:%S %Y"))
timeBegin = epoch_time  # - 3600 * 48
# timeEnd = epoch_time - 3600 * 45


check_input = True
while check_input:
    time_resolution = int(input("Enter the Time Resolution [seconds] e.g. 60: "))
    freq_resolution = int(input("Enter the Frequency Resolution [Hz] e.g. 100000: "))
    freqMin = int(input("Enter the Start Frequency [Hz] e.g. 80000000: "))
    freqMax = int(input("Enter the End Frequency [Hz] e.g. 90000000: "))

    duration =  int(input("Enter how many hours of spectrum measurement (max 6) e.g. 4: "))
    timeEnd = epoch_time + 3600 * duration

    # freq_resolution = int(4e6)
    # freqMin = int(25.00 * 1e6)
    # freqMax = int(1600.00 * 1e6)
    if time_resolution >= 60 and freq_resolution >= 10000 and freqMin >= int(25.00 * 1e6) and int(
            1600.00 * 1e6) >= freqMax > freqMin and 6 >= duration > 1:
        check_input = False
    else:
        print("Invalid input parameters for the Electrosense Aggregate API, check the documentation and repeat... \n")

sns.set_context("paper", rc={"font.size":20,"axes.titlesize":30,"axes.labelsize":30,
                             "xtick.labelsize" : 30,"ytick.labelsize" : 30})
response = get_spectrum_data(sensor_id_A, timeBegin, timeEnd, freqMin, freqMax, time_resolution, freq_resolution)
fig, ax = plt.subplots(1, 1, figsize=(15,10))
if (response != None):
     A = np.array([np.array(xi) for xi in response['values']])
     ax.imshow(A, aspect='auto', cmap=cm.jet)
     img = ax.imshow(A, aspect='auto',
                extent=[freqMin / 1e6, freqMax / 1e6, timeEnd, timeBegin],
                cmap=cm.jet)

     ylabels = [item.get_text() for item in ax.get_yticklabels()]
     date_values = np.arange(timeBegin, timeEnd, (timeEnd - timeBegin) / len(ylabels))
     date_text = [(time.strftime("%H:%M", time.gmtime(xi))) for xi in date_values]
     ylabels = date_text
     ax.set_yticklabels(ylabels)
     ax.set_title("Sensor %s" % sensor_name_A,pad=2)
     ax.set_xlabel('frequency (MHz)',fontsize=28)
     ax.set_ylabel('time',fontsize=28)
     c = plt.colorbar(img, ax=ax)
     c.set_label("Power (dB/Hz)",fontsize=24)

fig.tight_layout()
plt.savefig('./resources/Waterfall_%s.png'%sensor_name_A)
plt.show()