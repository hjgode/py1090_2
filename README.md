# py1090_2
analyse ads-b messages and send data to fhem

I am running a RTL-SDR ADS-B dongle and feed adsbox with aircraft data. adsbox further on sends ads-b messages on TCP/IP port 30003 which in turn can be used by other applications like py1090_2.

This code is based on the py1090 code and classes build by Jonas Lieb (https://github.com/jojonas/py1090)

The code has been extended and now records number of flights within a defined distance around a given location. These can give nice plots with aircraft activity around the ADS-B receiver:

https://raw.githubusercontent.com/hjgode/py1090_2/master/doc/fhem-flugdaten.png

The flight collection is cleaned up periodically using a last_seen property.

Additionally the flight absolute or view distance is calculated and will be used with a noise level detector value to record noise level and near flight data.

There is a local fhem log written all x minutes and noise data will be transmitted to fhem using a telnet connection.

The noise data will be read with each ADS-B message processed, either via a serial port (Arduino Nano) or TCP/IP (ESP-8266 or nodeMCU).
