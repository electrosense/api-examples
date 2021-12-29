# !/usr/bin/env python

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
import shutil
import json
import tempfile
import webbrowser
import optparse
import getpass

from requests.auth import HTTPBasicAuth

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
username = options.username
password = options.password

# Electrosense API
MAIN_URI = 'https://electrosense.org/api'
SENSOR_LIST = MAIN_URI + '/sensor/list/'

# Google maps URI
url = 'http://maps.google.com/maps/api/staticmap?center=46.1671105,3.7804881&zoom=5&size=1024x1024&maptype=roadmap&format=jpg&'

r = requests.get(SENSOR_LIST, auth=HTTPBasicAuth(username, password))
slist_json = json.loads(r.content)

markers = ""

for sensor in slist_json:
    color = "red"
    state = ""
    if (sensor['sensing']):
        color = "green"
        state = "S"

    markers = markers + "markers=color:" + color + "|label:" + state + "|" + str(
        sensor['position']['latitude']) + "," + str(sensor['position']['longitude']) + "&"

image_file = tempfile.gettempdir() + "/map.jpg"

r = requests.get(url + markers, stream=True)
if r.status_code == 200:
    with open(image_file, 'wb') as f:
        r.raw.decode_content = True
        shutil.copyfileobj(r.raw, f)

    webbrowser.open(image_file)

