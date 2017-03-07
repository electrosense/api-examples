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
#  Authors : Roberto Calvo <roberto [dot] calvo [at] imdea [dot] org)


import requests
import json
import time

from requests.auth import HTTPBasicAuth
from collections import OrderedDict
from urllib import urlencode

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
MAIN_URI ='https://test.electrosense.org/api'
SENSOR_LIST = MAIN_URI + '/sensor/list/'
SENSOR_AGGREGATED = MAIN_URI + "/spectrum/aggregated"

r = requests.get(SENSOR_LIST, auth=HTTPBasicAuth(username, password))

if r.status_code != 200:
    print r.content
    exit(-1)

slist_json = json.loads(r.content)


for i, sensor in enumerate(slist_json):
    print "[%d] %s (%d) - Sensing: %s" % (i, sensor['name'], sensor['serial'], sensor['sensing'])
    print str(sensor['serial']) + "," + str(sensor['position']['latitude']) + "," + str(sensor['position']['longitude'])

print ""
pos = int( raw_input("Please enter the sensor: "))

print ""
print "Asking for 20 hours of spectrum data : "
print "   %s (%d) - %s" % (slist_json[pos]['name'], slist_json[pos]['serial'], slist_json[pos]['sensing'])


# Ask for 5 minutes of aggregatd spectrum data

def get_spectrum_data (sensor_id, timeBegin, timeEnd, aggFreq, aggTime):
    
    params = OrderedDict([('sensor', sensor_id),
                          ('timeBegin', timeBegin),
                          ('timeEnd', timeEnd),
                          ('freqMin', int(24*1e6)),
                          ('freqMax', int(1766*1e6)),
                          ('aggFreq', aggFreq),
                          ('aggTime', aggTime),
                          ('aggFun','AVG')])


    r = requests.get(SENSOR_AGGREGATED, auth=HTTPBasicAuth(username, password), params=urlencode(params))

    
    if r.status_code == 200:
        return json.loads(r.content)
    else:
        print "Response: %d" % (r.status_code)
        return None

sp1 = None
sp2 = None
sp3 = None    

epoch_time = int(time.time())
timeBegin = epoch_time - (3600*24*2)
timeEnd = timeBegin + (3600*20*2)

response = get_spectrum_data (slist_json[pos]['serial'], timeBegin, timeEnd, int(2e6), 60*15)

date_values = np.arange(timeBegin, timeEnd, (timeEnd-timeBegin)/10)
date_text = np.array([ np.array (time.strftime("%H:%M:%S", time.gmtime(xi))) for xi in date_values])

if (response != None):       

    A = np.array([ np.array(xi) for xi in response['values'] ])

    sp1 = plt.subplot(311)
    plt.imshow(A)
    plt.title('Frequency Resolution: 2 MHz')    
    sp1.set_xticklabels ( np.array(map(str,(np.array(sp1.get_xticks().tolist())*2).tolist())).tolist())
    sp1.set_yticklabels (date_text)
    plt.colorbar()    

response = get_spectrum_data (slist_json[pos]['serial'], timeBegin, timeEnd, int(5e6), 60*15)

if (response != None):       

    A = np.array([ np.array(xi) for xi in response['values'] ])
    sp2 = plt.subplot(312)
    plt.imshow(A)
    plt.title('Frequency Resolution: 5 MHz')
    sp2.set_xticklabels ( np.array(map(str,(np.array(sp2.get_xticks().tolist())*5).tolist())).tolist())
    sp2.set_yticklabels (date_text)
    plt.colorbar()    
    
response = get_spectrum_data (slist_json[pos]['serial'], timeBegin, timeEnd, int(10e6), 60*15)

if (response != None):       

    A = np.array([ np.array(xi) for xi in response['values'] ])

    sp3 = plt.subplot(313)
    plt.imshow(A)
    plt.title('Frequency Resolution: 10 MHz')
    sp3.set_xticklabels ( np.array(map(str,(np.array(sp3.get_xticks().tolist())*10).tolist())).tolist())
    sp3.set_yticklabels (date_text)
    plt.colorbar()
    plt.show()
    

