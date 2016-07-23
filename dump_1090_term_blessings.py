from py1090.connection import *
from py1090.message import *
from py1090.collection import *
from py1090.helpers import *
from py1090.fhem import *

#using curses or blessings
USE_BLESSING=True
if USE_BLESSING:
    from py1090.display_blessing import *
else:
    from py1090.display import *
    from curses import wrapper

#import py1090
#import helpers 
import datetime
from time import time
from py1090.json_getnoise import *

# needs python3, python2.x will not work

USE_SERIAL=False
USE_NOISE=True #use serial port to read noise data
#SERIAL_PORT="/dev/pts/3"
        
USE_FHEM=True #use telnet to update noise data within fhem

MAX_DISTANCE=30 #km distance to log
MAX_ALTITUDE=5000  # m altitude to log
UPDATE_INTERVAL=1 #minutes to update log file

CLEANUP_TIMEOUT=1 #minutes a flight has to be last seen before cleanup
#local position
myLat = 51.0991
myLon = 6.5095

def cleanup(_flightcollection, _record_time):
    """find flights which last_seen older than 5 minutes and clean this
    returns Nothing
    """
    toremove=[]
    for f in _flightcollection:
        if f.last_seen:
            #print("last_seen: ", f.last_seen, datetime.datetime.now())
            tdiff=_record_time - f.last_seen
            if tdiff > datetime.timedelta(minutes=CLEANUP_TIMEOUT):
#                print("---- remove: ", f.hexident)
                toremove.append(f.hexident)
    for i in toremove:
        _flightcollection.remove(i)

    return

def filtercollection(_flightcollection, disp):
    """find flights which last_seen older than 5 minutes and clean this
    returns Nothing
    """
    toremove=[]
    for f in _flightcollection:
        lastDist=f.last_distance;
        if lastDist:
           if lastDist>MAX_DISTANCE:
               toremove.append(f.hexident)
    for i in toremove:
        _flightcollection.remove(i)
        disp.print_msg("DIST removed "+i+ "     ")

#    return;
	
    toremove=[]
    for f in _flightcollection:
        lastAltitude=f.last_altitude;
        if lastAltitude!=None:
            if lastAltitude*0.3048 > MAX_ALTITUDE: #alt is in feet, MAX_ALTITUDE is in m
               toremove.append(f.hexident)
    for i in toremove:
        _flightcollection.remove(i)
        disp.print_msg("ALT removed "+i+ "     ")
        
    return

#return flightcollectionentry with nearest view distance
def getnearest(_flightcollection):
    mynearest=None
    distmax=100000
    for flight in _flightcollection:
#                  if flight.hexident in blacklist_hexidents:
#                      continue
#                   print("flight: ", flight.last_altitude, flight.last_position, flight.last_seen)
#                   print("lowest: ", flight.lowest)
        #nearest returns entry with lowest view distance
        ndist, hid = flight.nearest()
        if ndist < distmax and hid:
            mynearest=flight
            distmax=ndist
##                       print("nearest: ", hid, ndist)
##                       print("distmax=",distmax)
    return mynearest

def record_positions_to_file(screen, filename):
    if USE_BLESSING==False:
        disp = display(screen)
    else:
        disp = display(screen)
    
    if USE_NOISE:
        mynoise = json_noise(disp.print_msg)
    collection = FlightCollection()
    starttime = time()
    minAlt = 100000
    if USE_SERIAL:
       try:
          serialdata=SerialData(SERIAL_PORT)
          serialdata.startreading()
       except:
          print("Serial Init failed")
      
    with Connection("atom2", 30003) as connection, open('message.log', 'a') as logmsg:
        file = open(filename, 'a')
        lines = 0
        for line in connection:
            logmsg.write(line)
            logmsg.flush()
            message = Message.from_string(line)
##            print("trans type: ", message.transmission_type, message.aircraft_id, message.flight_id, message.callsign)
            collection.add(message)
			
##            disp.add_line(line) '  use single msg add
            
            if message.record_time:
                cleanup(collection, message.record_time)
            filtercollection(collection, disp)
			#add noise measure to message data
            if USE_NOISE:
                n=mynoise.get_noise()
                message.set_noise(n)
				    
            disp.set_coll(collection,message.record_time)
            disp.print_msg(line)

            if message.latitude and message.longitude:# and message.altitude:
               kmdistance = distance_between(myLat, myLon, message.latitude, message.longitude) / 1000
               skm = (' dist: %.2f km' % kmdistance).replace(',','.')
##               print (skm)
               snearest=" nearest: "
               sDateTime = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
               if kmdistance < MAX_DISTANCE:
                   # 2014-12-05_07:10:58 flugdaten anzahl:23
                   sDateTime = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
                   sAlt=" alt: "
                   if message.altitude:
                       ialt = message.altitude*0.3048
                       alt = ('%.2f' % (message.altitude*0.3048)).replace(',','.')
                       sAlt=" alt: " + alt + " m"
                       if minAlt>ialt:
                           minAlt=ialt #save lowest altitude
                       #get flight with nearest view distance
                       mynearest=getnearest(collection)
                       if mynearest:
                           snearest+= ("%.2f" % mynearest.abs_distance)
                           #if USE_NOISE:
                           #    mynearest._noise=getdata()
                           ndist, hid = mynearest.nearest()
##                       print("nearest: ", mynearest.hexident, mynearest.callsign, ndist, mynearest._noise)
                   #print("flight: ", flight)
                   #path = list(flight.path)
##                   print(sDateTime + " flugdaten anzahl: " + str(len(collection)) + skm + sAlt + snearest)
               lines += 1          
##               print("Recorded lines:", lines)
##               print("msg: ",message.to_string())
               
##               print("flights: ", len(collection))
               end_time = time()
               time_taken = end_time - starttime # time_taken is in seconds
               hours, rest = divmod(time_taken,3600)
               minutes, seconds = divmod(rest, 60)
               if minutes >= UPDATE_INTERVAL: #5:
                   if mynearest:
                       if USE_FHEM:
                           #TODO add a callback function that we can use to add print output of fhem to curses screen
                           senddata(mynearest.callsign, ndist, mynearest.noise, disp.print_msg)
                   starttime=time()
##                   print("fileLog: " + sDateTime + " flugdaten anzahl: " + str(len(collection)) + skm + sAlt + snearest)
                   file.write(sDateTime + " flugdaten anzahl: " + str(len(collection)) + skm + sAlt + snearest + '\n')
                   file.flush()
#                   collection=FlightCollection() #clear
                   minAlt=100000
                   # check for month roll-over and use new file
                   if filename != "/opt/fhem/log/FileLog_Flugdaten-" + datetime.datetime.now().strftime('%Y-%m') + ".log":
                       file.flush()
                       file.close()
                       filename = "/opt/fhem/log/FileLog_Flugdaten-" + datetime.datetime.now().strftime('%Y-%m') + ".log"
                       file=open(filename, 'a')
def main(screen):
    sfile = "/opt/fhem/log/FileLog_Flugdaten-" + datetime.datetime.now().strftime('%Y-%m') + ".log"
    record_positions_to_file(screen, sfile)
    
if __name__ == "__main__":
    if USE_BLESSING:
        main(None)
    else:
        wrapper(main)
