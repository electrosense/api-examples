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

    
# Main

epoch_time = int(time.time())
#timeBegin = epoch_time - (3600*24*4) - 3600*8
#timeEnd = timeBegin + (3600*23*1)

timeBegin=1481334714 #1481331114
timeEnd=1481406714#1481403114


sensors_id = [202481594668072 ,202481592720557]
sensors_loc = ['Madrid (Spain)', 'Leuven (Belgium)']
plot_id = [211, 212]

for i, s in enumerate(sensors_id):

    response = get_spectrum_data (sensors_id[i], timeBegin, timeEnd, int(4e6), 60*15)

        
    if (response != None):       

        A = np.array([ np.array(xi) for xi in response['values'] ])
        
        sp1 = plt.subplot(plot_id[i])
        plt.imshow(A)
        plt.title('Spectrum usage (' + time.strftime("%D", time.gmtime(timeBegin)) + ') - ' + sensors_loc[i])
        
        sp1.set_xticklabels ( np.array(map(str,(np.array(sp1.get_xticks().tolist())*4).tolist())).tolist())
        plt.xlabel('Frequency (MHz)')
        
        date_values = np.linspace(timeBegin, timeEnd, (len(sp1.get_yticklabels())-2))
        date_text = np.array([ np.array (time.strftime("%H:%M:%S", time.gmtime(xi))) for xi in date_values])
        date_text = np.insert(date_text, 0, '')
        date_text = np.append(date_text, '')
        #print date_values
        #print date_text
        sp1.set_yticklabels (date_text)

        plt.colorbar()    



plt.show()
    

