#!/bin/bash

ppm=66
wxdevice=9
timer=570

timestamp() {
  date +"%D %T"
}

timestamp > /var/tmp/wx.txt
sudo timeout $timer rtl_433 -p $ppm -R $wxdevice >> /var/tmp/wx.txt
python wx.py
