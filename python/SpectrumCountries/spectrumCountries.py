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


def get_spectrum_data(sensor_id, timeBegin, timeEnd, freq_min, freq_max, aggTime, aggFreq):
    params = OrderedDict([('sensor', sensor_id),
                          ('timeBegin', timeBegin),
                          ('timeEnd', timeEnd),
                          ('freqMin', freq_min),
                          ('freqMax', freq_max),
                          ('aggFreq', aggFreq),
                          ('aggTime', aggTime),
                          ('aggFun', 'AVG')])

    try:
        r = requests.get(SENSOR_AGGREGATED, auth=HTTPBasicAuth(username, password), params=urlencode(params))
        print(r.url)
        print(r.status_code)
        print(r.content)

        if r.content == b'':
            raise NameError('NoSpectrum')

        if r.status_code == 200:
            return json.loads(r.content)
        else:
            print("Response: %d" % (r.status_code))
            return None
    except NameError:
        print("No Spectrum data in this period... try another day")

    except Exception as error:
        print(error)
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
    print(count_active_sensor, sname, sserial)
    count_active_sensor += 1


print(" \n Select two sensors to compare spectrum data \n")
sensor1 = int(input("Enter first sensor from the list  "))  # 28
sensor2 = int(input("Enter second sensor from the list  "))  # 60


sensor_id_A, sensor_id_B = sensing_sensors_list[sensor1]['serial'],sensing_sensors_list[sensor2]['serial']
sensor_name_A, sensor_name_B = sensing_sensors_list[sensor1]['name'],sensing_sensors_list[sensor2]['name']
sensor_country_A, sensor_country_B = sensing_sensors_list[sensor1]['country'],sensing_sensors_list[sensor2]['country']

check_day = True
now = datetime.datetime.now()
while check_day:
    day = input("Enter the day [dd]  ")
    month = input("Enter the month [mm]  ")
    year = input("Enter the year [yyyy]  ")

    if int(day) < 31 and int(month) <= 12 and int(year) <= now.year:
        check_day = False
    elif int(month) == 2 and int(day) > 28:
        print("Please insert a true date")
    else:
        print("Please insert a true date")


timestr = month+" "+day+" "+"10:00:00 "+year
calendar.timegm(time.strptime(timestr, "%m %d %H:%M:%S %Y"))


# epoch_time = 1599300000
epoch_time = calendar.timegm(time.strptime(timestr, "%m %d %H:%M:%S %Y"))
timeBegin = epoch_time  # - 3600 * 48
# timeEnd = epoch_time - 3600 * 45
timeEnd = epoch_time + 3600 * 3

sensors_id = [sensor_id_A, sensor_id_B]
sensors_loc = [sensor_country_A, sensor_country_B]
plot_id = [211, 212]

time_resolution = 60
freq_resolution = int(4e6)

freqMin = int(25.00 * 1e6)
freqMax = int(1600.00 * 1e6)

fig, ax = plt.subplots(2, 1, figsize=(20,13))
plt.suptitle('Spectrum usage (' + time.strftime("%d %b %Y", time.gmtime(timeBegin))+')', y=1.0)
response = get_spectrum_data(sensor_id_A, timeBegin, timeEnd, freqMin, freqMax, time_resolution, freq_resolution)

if (response != None):
    try:
        if [] in response['values'] or 'null' in response['values']:
            raise NameError('NullPSD')
        A = np.array([np.array(xi) for xi in response['values']])
        ax[0].imshow(A, aspect='auto', cmap=cm.jet)
        img = ax[0].imshow(A, aspect='auto',
                    extent=[freqMin / 1e6, freqMax / 1e6, timeEnd, timeBegin],
                    cmap=cm.jet)

        ylabels = [item.get_text() for item in ax[0].get_yticklabels()]
        date_values = np.arange(timeBegin, timeEnd, (timeEnd - timeBegin) / len(ylabels))
        date_text = [(time.strftime("%H:%M", time.gmtime(xi))) for xi in date_values]
        ylabels = date_text
        ax[0].set_yticklabels(ylabels)
        ax[0].set_title("Sensor %s" % sensor_name_A,pad=2)
        # ax[0].set_xlabel('frequency (MHz)')
        ax[0].set_ylabel('time')
        c = plt.colorbar(img, ax=ax[0])
        c.set_label("Power (dB)")
    except NameError:
        print("Warning: during this period some PSD information are missed, try another day.")
    except Exception as error:
        print(error)


response = get_spectrum_data(sensor_id_B, timeBegin, timeEnd, freqMin, freqMax, time_resolution, freq_resolution)
date_values = np.arange(timeBegin, timeEnd, (timeEnd - timeBegin) / 10)
date_text = np.array([np.array(time.strftime("%H:%M", time.gmtime(xi))) for xi in date_values])
if (response != None):
    try:
        if [] in response['values'] or 'null' in response['values']:
            raise NameError('NullPSD')
        A = np.array([np.array(xi) for xi in response['values']])
        ax[1].imshow(A, aspect='auto', cmap=cm.jet)
        img = ax[1].imshow(A, aspect='auto',
                extent=[freqMin / 1e6, freqMax / 1e6, timeEnd, timeBegin],
                cmap=cm.jet)
        ylabels = [item.get_text() for item in ax[0].get_yticklabels()]
        date_values = np.arange(timeBegin, timeEnd, (timeEnd - timeBegin) / len(ylabels))
        date_text = [(time.strftime("%H:%M", time.gmtime(xi))) for xi in date_values]
        ylabels = date_text
        ax[1].set_yticklabels(ylabels)
        ax[1].set_title("Sensor %s" % sensor_name_B,pad=2)
        ax[1].set_xlabel('frequency (MHz)')
        ax[1].set_ylabel('time')
        c = plt.colorbar(img, ax=ax[1])
        c.set_label("Power (dB)")
        fig.tight_layout()
        plt.savefig('./resources/output_spec_countries.png')
        plt.show()
    except NameError:
        print("Warning: during this period some PSD information are missed. Can't plot the entire spectrogram, try another day.")
    except Exception as error:
        print(error)
        print("Warning: during this period some PSD information are missed. Can't plot the entire spectrogram, try another day.")



    

