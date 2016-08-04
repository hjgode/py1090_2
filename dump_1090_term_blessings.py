from py1090.connection import *
from py1090.message import *
from py1090.collection import *
from py1090.helpers import *
from py1090.fhem import *

from py1090.config import *

#TODO: use different collections for fhem (every minute) and filelog (every hour)

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
    if not USE_FILTER:
        return
    """find flights which last_seen older than 5 minutes and clean this
    returns Nothing
    """
    toremove=[]
    for f in _flightcollection:
        lastDist=f.last_distance;
        if lastDist!=None:
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
        #nearest returns entry with lowest view distance
        ndist, hid = flight.nearest()
        if ndist < distmax and hid:
            mynearest=flight
            distmax=ndist
##                       print("nearest: ", hid, ndist)
##                       print("distmax=",distmax)
    return mynearest

def record_positions_to_file(screen, filename):
    minutes_for_log=0
    if USE_BLESSING==False:
        disp = display(screen)
    else:
        disp = display(screen)
    
    if USE_NOISE:
        mynoise = json_noise(disp.print_msg)
    collection = FlightCollection()
    collection_hour = FlightCollection() # second collection to cout airplanes per hour
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
            #add noise measure to message data
            if USE_NOISE:
                n=mynoise.get_noise()
                message.set_noise(n)
##            print("trans type: ", message.transmission_type, message.aircraft_id, message.flight_id, message.callsign)
            collection.add(message)
            collection_hour.add(message)
##            disp.add_line(line) '  use single msg add
            
            if message.record_time:
                cleanup(collection, message.record_time)
            filtercollection(collection, disp)
                    
            disp.set_coll(collection,message.record_time)
            disp.print_msg(line)

            if message.latitude and message.longitude:# and message.altitude:
               kmdistance = distance_between(myLat, myLon, message.latitude, message.longitude) / 1000
               skm = (' dist: %.2f km' % kmdistance).replace(',','.')
##               print (skm)
               snearest=" nearest: "
               mynearest=None
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
                       if mynearest != None:
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
               if minutes >= UPDATE_INTERVAL: #1:
                   if mynearest != None:
                       if USE_FHEM:
                           senddata(mynearest.callsign, ndist, mynearest.noise, disp.print_msg, mynearest.min_ground_speed)
                   starttime=time()
                   minutes_for_log+=1
                   #write filelog UPDATE_INTERVAL_LOG
                   if (minutes_for_log > UPDATE_INTERVAL_LOG):
                       minutes_for_log=0
                       mynearest_hour=getnearest(collection_hour)
                       snearest_hour=" nearest: "
                       if mynearest_hour != None:
                           snearest_hour+= ("%.2f" % mynearest_hour.abs_distance)
    ##                   print("fileLog: " + sDateTime + " flugdaten anzahl: " + str(len(collection)) + skm + sAlt + snearest)
                       file.write(sDateTime + " flugdaten anzahl: " + str(len(collection_hour)) + snearest + '\n')
                       file.flush()
                       collection_hour=FlightCollection() # clear
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
