#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

import array
import json
import os
import datetime
import os.path

stationid="xxxxxxxxx"
password="xxxxxxxxx"

wxdata = {}

#f = open("wx.txt")

keywords = ["wind speed", "temp", "humidity", "wind direction", "rain gauge", "dew point"]
webkeywords = {"wind speed":"windspeedmph", "temp":"tempf", "humidity":"humidity", "wind direction":"winddir", "rain gauge":"rainin", "dew point":"dewptf", "rainfall":"dailyrainin", "wind gust speed":"windgustmph", "wind gust direction":"windgustdir"}
stripchars = ['kph', '° F', '\xc2\xb0 F', '% RH', '°', '\xc2\xb0', 'in.']
HTMLEscapeChars = {':':'%3A'}

winddir = []
windspeed = []

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

#print windspeed
#print winddir

wxdata["wind speed"] = sum(windspeed) / float(len(windspeed))
wxdata["wind direction"] = sum(winddir) / float(len(winddir))
wxdata["wind gust speed"] = max(windspeed)

print len(winddir), len(windspeed)
for i in range(len(windspeed) - (len(windspeed) % 2)):
	if (windspeed[i] == wxdata["wind gust speed"]):
		wxdata["wind gust direction"] = winddir[int(i/2)]


#print 'windspeed', wxdata["wind speed"]
#print 'winddir', wxdata["wind direction"]
#print 'windgustspd', wxdata["wind gust speed"]
#print 'windgustdir', wxdata["wind gust direction"]

rainfallfile = "/tmp/rainfall-" + datetime.datetime.today().strftime("%Y-%m-%d") + ".txt"
rainfall = 0
if os.path.exists(rainfallfile):
	f = open(rainfallfile).read().strip()
	if( f != "" ):
		rainfall = float(f)

wxdata["rainfall"] = rainfall + wxdata["rain gauge"]
open(rainfallfile, 'w').write(str(wxdata["rainfall"]))

wxdata["dew point"] = (wxdata["temp"]-(9*(100-wxdata["humidity"])/25))

#print wxdata["temp"]-((9/25)*(100-wxdata["humidity"]))

print wxdata

for s,n in HTMLEscapeChars.iteritems():
	date = date.replace(s, n)

datastr = "action=updateraw&ID="+stationid+"&PASSWORD="+password+"&dateutc="+date

for w, x in wxdata.iteritems():
	if( w == "wind speed" ):
		x = x * 0.621371
	elif( w == "wind gust speed" ):
		x = x * 0.621371
	datastr += "&" + webkeywords[w] + "=" + str(x)

print datastr

with open('wxdata.txt', 'w') as fp:
	json.dump(wxdata, fp, indent=4)

#with open('/var/' + datetime.datetime.fromtimestamp(datetime.datetime.utcnow()).strftime('%Y-%m-%d'), 'w') as fp:
#	json.dump(wxdata['rain gauge'], fp)


import urllib2
req = urllib2.Request("http://weatherstation.wunderground.com/weatherstation/updateweatherstation.php?" + datastr)
r = urllib2.urlopen(req)

print r.read()

#os.system("rm wx.txt")

#os.system("bash ftp.sh wx.txt")
