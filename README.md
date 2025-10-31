# python-maschine-mk1-midi
Stop e-waste, save your Native Instruments Maschine MK1 Controller.

This is an easy way of getting your old MK1 back and running on Linux. 
Your MK1 controller is connected and found using **lsusb | grep -i maschine**
so you can run **sudo evtest** and select the Maschine Controller.
Press the pads, note the **event number** (*e.g. /dev/input/event10*) and codes (*Event: time 1761935823.462891, type 3 (EV_ABS), code 36 (?), value 1
*).
You might need to adjust the script.

This requires **Python3** - also install **python3-evdev python3-rtmidi**
Either adjust the CONFIG section of the script to your event number and pads or just run it using **sudo python3 maschine2midi.py** and you should see the input of your pads sent as midi.

Also see **python_maschine_mk1-v3.json** which is a layout for [Bespoke Synth](https://github.com/BespokeSynth/BespokeSynth) and should be placed in /Bespoke/controllers on your system. Also this might need adjustment for the pads - I only have one MK1. 


**tl;dr** sudo python3 maschine2midi.py
