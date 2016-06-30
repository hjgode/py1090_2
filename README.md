# py1090_2
analyse ads-b messages and send data to fhem

This code is based on the py1090 code and classes build by Jonas Lieb (https://github.com/jojonas/py1090)

The code has been extended and now records number of flights within a defined distance around a given location.

The flight collection is cleaned up periodically using a last_seen property.

Additionally the flight absolute or view distance is calculated and will be used with a noise level detector value to record noise level and near flight data.

There is a local fhem log written all x minutes and noise data will be transmitted to fhem using a telnet connection.

The noise data will be read with each ADS-B message processed, either via a serial port (Arduino Nano) or TCP/IP (ESP-8266 or nodeMCU).
