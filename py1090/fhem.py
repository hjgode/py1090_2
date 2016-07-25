#modul fhem.py
import telnetlib
import threading

"""
setreading     <devspec> <reading> <value>                       
               set reading for <devspec>
setstate       <devspec> <state>                                 
               set the state shown in the command list
ie: 
setreading fluglaerm distance x
setreading fluglaerm callsign y
setreading fluglaerm noise z
-or, in one line-
setreading fluglaerm distance x; setreading fluglaerm callsign y; setreading fluglaerm noise z
-and-
setstate fluglaerm z
"""

def strformat(value):
    str = ('%.2f' % value).replace(',','.')
    return str
    
def senddata0(flight, viewdistance, noise, callback, ground_speed):
    callback("senddata: {0} {1} {2}".format(flight, viewdistance, noise))
    try:
        tn=telnetlib.Telnet("atom2", 7072, 3)
        #tn.read_until("is '^]'.".encode(),2)
        #tn.read_all()
        tn.write("\n".encode())
        tn.read_until("fhem> ".encode(),2)
           
        #send data now
        data="setreading fluglaerm distance "+strformat(viewdistance)+ "; setreading fluglaerm callsign "+flight+"; setreading fluglaerm noise "+strformat(noise)+";"+"; setreading fluglaerm ground_speed "+strformat(ground_speed)+";"
        tn.write(data.encode())    
        tn.read_until("fhem> ".encode(),2)
            
        tn.write("exit\n".encode())
        callback (tn.read_all())
        tn.close()
    except:
        callback("exception in telnet read/write")
    callback("senddata done.")
    return
    
def senddata(flight, viewdistance, noise, callback, ground_speed):
    callback("senddata: {0} {1} {2}".format(flight, viewdistance, noise))
    thread = threading.Thread(target=senddata0, args=(flight, viewdistance, noise, callback, ground_speed))
    thread.daemon=True # let's terminat with CTRL+C in main
    thread.start()
