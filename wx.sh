#!/bin/bash

ppm=66 #ppm measured with rtl_test
wxdevice=9 #acurite 5n1 code
timer=570 #how long should we listen to the radio before we submit data

timestamp() {
  date +"%D %T"
}

timestamp > /var/tmp/wx.txt #This timestamp is almost entirely used for debugging
sudo timeout $timer rtl_433 -p $ppm -R $wxdevice >> /var/tmp/wx.txt
python wx.py
