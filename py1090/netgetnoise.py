#modul netgetnoise.py
import telnetlib

"""
nodemcu socket server gives back current noise level
"""

server="192.168.0.102" # nodemcu address
port=43333

def strformat(value):
    str = ('%.2f' % value).replace(',','.')
    return str
    
def getdata():
    print("getdata: ...")
    try:
        tn=telnetlib.Telnet(server, port, 3)
        #tn.read_until("is '^]'.".encode(),2)
        #tn.read_all()
        #tn.write("\n".encode())
        tn.read_until("Noise >".encode(),2)
           
        #send data now
        data="GET\n";
        tn.write(data.encode())
        noiseB = tn.read_until("\n".encode());
        print ("noise: ", noiseB.decode());    
        tn.read_until("Noise >".encode(),2)
            
        tn.write("exit\n".encode())
        print (tn.read_all())
        tn.close()
    except:
        print("exception in telnet read/write")
    print("getdata done.")
    return int(noiseB.decode().strip());
    
