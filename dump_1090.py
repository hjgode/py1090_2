from py1090.connection import *
from py1090.message import *
from py1090.collection import *
from py1090.helpers import *
from py1090.fhem import *

#import py1090
#import helpers 
import datetime
from time import time
# needs python3, python2.x will not work
        
def cleanup(_flightcollection, _record_time):
    """find flights which last_seen older than 5 minutes and clean this
    returns Nothing
    """
    toremove=[]
    for f in _flightcollection:
        if f.last_seen:
            #print("last_seen: ", f.last_seen, datetime.datetime.now())
            tdiff=_record_time - f.last_seen
            if tdiff > datetime.timedelta(minutes=1):
                print("---- remove: ", f.hexident)
                toremove.append(f.hexident)
    for i in toremove:
        _flightcollection.remove(i)

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
#                       print("nearest: ", hid, ndist)
#                       print("distmax=",distmax)
    return mynearest

def record_positions_to_file(filename):
    collection = FlightCollection()
    starttime = time()
    myLat = 51.0991
    myLon = 6.5095
    minAlt = 100000
    with Connection("atom2", 30003) as connection, open(filename, 'a') as file, open('message.log', 'a') as logmsg:
        lines = 0
        for line in connection:
            logmsg.write(line)
            logmsg.flush()
            message = Message.from_string(line)
#            print("trans type: ", message.transmission_type, message.aircraft_id, message.flight_id, message.callsign)
            collection.add(message)
            if message.record_time:
                cleanup(collection, message.record_time)

            if message.latitude and message.longitude:# and message.altitude:
               kmdistance = distance_between(myLat, myLon, message.latitude, message.longitude) / 1000
               skm = (' dist: %.2f km' % kmdistance).replace(',','.')
               print (skm)
               if kmdistance < 1000:
                   # 2014-12-05_07:10:58 flugdaten anzahl:23
                   sDateTime = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
                   sAlt=" alt: "
                   if message.altitude:
                       ialt = message.altitude*0.3048
                       alt = ('%.2f' % (message.altitude*0.3048)).replace(',','.')
                       sAlt=" alt: " + alt + " m"
                       if minAlt>ialt:
                           minAlt=ialt
#                   file.write(sDateTime + " flugdaten anzahl: " + str(len(collection)) + skm + sAlt + '\n')
#                   file.flush()
                   print(sDateTime + " flugdaten anzahl: " + str(len(collection)) + skm + sAlt)
                   lines += 1          
                   print("Recorded lines:", lines)
               print("msg: ",message.to_string())
               
               print("flights: ", len(collection))
               #get flight with nearest view distance
               mynearest=getnearest(collection)
               if mynearest:
                   ndist, hid = mynearest.nearest()
                   print("nearest: ", mynearest.hexident, mynearest.callsign, ndist)
                   #print("flight: ", flight)
                   #path = list(flight.path)
               end_time = time()
               time_taken = end_time - starttime # time_taken is in seconds
               hours, rest = divmod(time_taken,3600)
               minutes, seconds = divmod(rest, 60)
               if minutes >= 1: #5:
                   if mynearest:
                       senddata(mynearest.callsign, ndist, 70)
                   starttime=time()
                   file.write(sDateTime + " flugdaten anzahl: " + str(len(collection)) + skm + sAlt + '\n')
                   file.flush()
#                   collection=FlightCollection() #clear
                   minAlt=100000
if __name__ == "__main__":
    sfile = "/opt/fhem/log/FileLog_Flugdaten-" + datetime.datetime.now().strftime('%Y-%m') + ".log"
    record_positions_to_file(sfile)
    
