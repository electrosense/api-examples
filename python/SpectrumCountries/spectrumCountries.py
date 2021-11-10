#!/usr/bin/env python

#  Copyright (C) IMDEA Networks Institute 2016
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see http://www.gnu.org/licenses/.
#
#  Authors : Alessio Scalingi <alessio [dot] scalingi [at] imdea [dot] org)
#            Roberto Calvo <roberto [dot] calvo [at] imdea [dot] org)
#

import requests
import json
import time
from urllib.parse import urlencode
from requests.auth import HTTPBasicAuth
from collections import OrderedDict

from matplotlib import cm
import matplotlib.pyplot as plt
import numpy as np
import optparse
import getpass

parser = optparse.OptionParser("usage: %prog -u <username> [-p <password>]")
parser.add_option("-u", "--user", dest="username",
                  type="string",
                  help="API username")
parser.add_option("-p", "--pass", dest="password",
                    type="string", help="API password")

(options, args) = parser.parse_args()
if not options.username:
   parser.error("Username not specified")

if not options.password:
   options.password = getpass.getpass('Password:')

# Electrosense API Credentials 
username=options.username
password=options.password

# Electrosense API
MAIN_URI ='https://electrosense.org/api'
SENSOR_LIST = MAIN_URI + '/sensor/list/'
SENSOR_AGGREGATED = MAIN_URI + "/spectrum/aggregated"


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
# Scritto il codicde nella versione di python 3.
#Prima cosa---- selezionare i sensori dall' utente invece di selezionare i sensori coding,
# aggiungendo la logica per selezionare solamente i sensori che sono "sensing" invece di selezionare i sensory hard coded.
# fix labels on the y axes accordig to the time



# Main
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


print(" \n Select two sensors to explore the spectrum \n")
sensor1 = int(input("Enter first sensor to compare"))  # 28
sensor2 = int(input("Enter second sensor to compare"))  # 60


sensor_id_A, sensor_id_B = sensing_sensors_list[sensor1]['serial'],sensing_sensors_list[sensor2]['serial']
sensor_name_A, sensor_name_B = sensing_sensors_list[sensor1]['name'],sensing_sensors_list[sensor2]['name']
sensor_country_A, sensor_country_B = sensing_sensors_list[sensor1]['country'],sensing_sensors_list[sensor2]['country']

epoch_time = int(time.time())
epoch_time = 1599300000
timeBegin = epoch_time - 3600 * 48
timeEnd = epoch_time - 3600 * 45

sensors_id = [sensor_id_A, sensor_id_B]
sensors_loc = [sensor_country_A, sensor_country_B]
plot_id = [211, 212]

time_resolution = 60
freq_resolution = int(4e6)

freqMin = int(25.00 * 1e6)
freqMax = int(1600.00 * 1e6)

fig, ax = plt.subplots(2, 1)
plt.suptitle('Spectrum usage (' + time.strftime("%d %b %Y", time.gmtime(timeBegin))+')',y=1.0)
response = get_spectrum_data(sensor_id_A, timeBegin, timeEnd, freqMin, freqMax, time_resolution, freq_resolution)

if (response != None):
     A = np.array([np.array(xi) for xi in response['values']])
     ax[0].imshow(A, aspect='auto', cmap=cm.jet)
     img = ax[0].imshow(A, aspect='auto',
                extent=[freqMin / 1e6, freqMax / 1e6, timeEnd, timeBegin],
                cmap=cm.jet)

     ylabels = [item.get_text() for item in ax[0].get_yticklabels()]
     date_values = np.arange(timeBegin, timeEnd, (timeEnd - timeBegin) / len(ylabels))
     date_text = [(time.strftime("%H:%M", time.gmtime(xi))) for xi in date_values]
     date_text
     ylabels = date_text
     ax[0].set_yticklabels(ylabels)
     ax[0].set_title("Sensor %s" % sensor_name_A,pad=2)
     # ax[0].set_xlabel('frequency (MHz)')
     ax[0].set_ylabel('time')
     c = plt.colorbar(img, ax=ax[0])
     c.set_label("Power (dB)")


response = get_spectrum_data(sensor_id_B, timeBegin, timeEnd, freqMin, freqMax, time_resolution, freq_resolution)
date_values = np.arange(timeBegin, timeEnd, (timeEnd - timeBegin) / 10)
date_text = np.array([np.array(time.strftime("%H:%M", time.gmtime(xi))) for xi in date_values])
if (response != None):
     A = np.array([np.array(xi) for xi in response['values']])
     ax[1].imshow(A, aspect='auto', cmap=cm.jet)
     img = ax[1].imshow(A, aspect='auto',
                extent=[freqMin / 1e6, freqMax / 1e6, timeEnd, timeBegin],
                cmap=cm.jet)
     ylabels = [item.get_text() for item in ax[0].get_yticklabels()]
     date_values = np.arange(timeBegin, timeEnd, (timeEnd - timeBegin) / len(ylabels))
     date_text = [(time.strftime("%H:%M", time.gmtime(xi))) for xi in date_values]
     date_text
     ylabels = date_text
     ax[1].set_yticklabels(ylabels)
     ax[1].set_title("Sensor %s" % sensor_name_B,pad=2)
     ax[1].set_xlabel('frequency (MHz)')
     ax[1].set_ylabel('time')
     c = plt.colorbar(img, ax=ax[1])
     c.set_label("Power (dB)")

fig.tight_layout()
#plt.savefig('./resources/output.png')
plt.show()
    

