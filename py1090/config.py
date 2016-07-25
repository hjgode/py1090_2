#global config

USE_SERIAL=False
USE_NOISE=True #use serial port to read noise data
#SERIAL_PORT="/dev/pts/3"
        
USE_FHEM=True #use telnet to update noise data within fhem

MAX_DISTANCE=30 #km distance to log
MAX_ALTITUDE=5000  # m altitude to log
UPDATE_INTERVAL=1 #minutes to update log file

CLEANUP_TIMEOUT=1 #minutes a flight has to be last seen before cleanup
#local position
myLat=51.133858
#myLat = 51.0991
myLon=6.511662
#myLon = 6.5095

USE_FILTER=True #filter flights by altitude and distance?
#using curses or blessings
USE_BLESSING=True
