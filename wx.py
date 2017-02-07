#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

import array
import json
import os
import datetime
import os.path

#account info is sent as a plaintext POST message so I'm not even going to bother with best practices when it comes to storing passwords
stationid="xxxxxxxxx"
password="xxxxxxxxx"

wxdata = {}

#keywords from the rtl_433 text dump we want
keywords = ["wind speed", "temp", "humidity", "wind direction", "rain gauge", "dew point"]

#convert keywords from the RF stream to wunderground-usable key-values
webkeywords = {"wind speed":"windspeedmph", "temp":"tempf", "humidity":"humidity", "wind direction":"winddir", "rain gauge":"rainin", "dew point":"dewptf", "rainfall":"dailyrainin", "wind gust speed":"windgustmph", "wind gust direction":"windgustdir"}

#Get rid of these characters
stripchars = ['kph', '° F', '\xc2\xb0 F', '% RH', '°', '\xc2\xb0', 'in.']

#convert these characters to html escape characters, probably a programmatic method I could have used.
HTMLEscapeChars = {':':'%3A'}

winddir = []
windspeed = []

#Crazy for-loop
date = str(datetime.datetime.utcnow().strftime("%Y-%m-%d+%H:%M:%S"))
for l in open("wx.txt"):
	values = l.split(",")
	for v in values:
		v = v.strip()
		for s in stripchars:
			v = v.replace(s, "").strip()
		for k in keywords:
			if not k in wxdata:
				wxdata[k] = 0
			if v.startswith(k):
				if( k == "wind direction" ):
					winddir.append(float(v.replace(k + ":", "").strip()))
				elif( k == "wind speed" ):
					windspeed.append(float(v.replace(k + ":", "").strip()))
				else:
					wxdata[k] = float(v.replace(k + ":", "").strip())

#Wind data, we want the max and average for wind gust/speed records
wxdata["wind speed"] = sum(windspeed) / float(len(windspeed))
wxdata["wind direction"] = sum(winddir) / float(len(winddir))
wxdata["wind gust speed"] = max(windspeed)

#wind direction is only given every other RF message
print len(winddir), len(windspeed)
for i in range(len(windspeed) - (len(windspeed) % 2)):
	if (windspeed[i] == wxdata["wind gust speed"]):
		wxdata["wind gust direction"] = winddir[int(i/2)]

#Keep a running tally of how much rainfall we've had this day
#read the rainfall we've already had today
rainfallfile = "/tmp/rainfall-" + datetime.datetime.today().strftime("%Y-%m-%d") + ".txt"
rainfall = 0
if os.path.exists(rainfallfile):
	f = open(rainfallfile).read().strip()
	if( f != "" ):
		rainfall = float(f)

#how much rainfall has happened today
wxdata["rainfall"] = rainfall + wxdata["rain gauge"]

#commit new rainfall amounts to our running tally
open(rainfallfile, 'w').write(str(wxdata["rainfall"]))

#Perform this poorly understood mathematical operation to get dew point
wxdata["dew point"] = (wxdata["temp"]-(9*(100-wxdata["humidity"])/25))

#debug
print wxdata

#escape HTML characters
for s,n in HTMLEscapeChars.iteritems():
	date = date.replace(s, n)

#Form the base of the html POST, send password in plaintext like a boss
datastr = "action=updateraw&ID="+stationid+"&PASSWORD="+password+"&dateutc="+date

#convert from metric to imperial because that makes sense
for w, x in wxdata.iteritems():
	if( w == "wind speed" ):
		x = x * 0.621371
	elif( w == "wind gust speed" ):
		x = x * 0.621371
	datastr += "&" + webkeywords[w] + "=" + str(x)

print datastr

#save this for debug
with open('wxdata.txt', 'w') as fp:
	json.dump(wxdata, fp, indent=4)

#send!
import urllib2
req = urllib2.Request("http://weatherstation.wunderground.com/weatherstation/updateweatherstation.php?" + datastr)
r = urllib2.urlopen(req)

print r.read()
