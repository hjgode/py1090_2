# serial class to get noise level
import serial
import threading

"""
terminal 1
socat -d -d pty,raw,echo=0 pty,raw,echo=0

terminal 2
cat < /dev/pts/3

terminal 3
echo "65" > /dev/pts/4
"""

class SerialData:
    def __init__(self, p):
        self.is_alive=True
        self.noiselevel=60
        self.connected=False
        self.port=p
        self.thread=None
        try:
            self.serial=serial.Serial(p, 115200, timeout=None)
        except:
            print("### Serialport Exception")
            self.serial=None
            

    def __del__(self):
        self.is_alive=False
        #if self.thread:
        #    self.thread.join()
        
    def get_noiselevel(self):
        return self.noiselevel
        
    def handle_data(self,data):
        print("noise: ",data)
        self.noiselevel=data

    def close(self):
        self.serial.close()
        
    def read_from_port(self):
        try:
            str=""
            while self.is_alive:
                if self.serial:
                    read=self.serial.read() #blocks
                    print("### serial: ",read.decode())
                    if read.decode() == '\n' or read.decode() == '\r':
                        print("### serial NewLine")
                        try:
                            print("### int() on ",str)
                            data=int(str)
                        except ValueError:
                            data=0
                        self.handle_data(data)
                        str=""
                    else:
                        str+=read.decode()
        except serial.SerialException:
            self.is_alive=False
            print("Exception in serial")
        return
               
    def startreading(self):
        self.thread = threading.Thread(target=self.read_from_port)
        self.thread.daemon=True # let's terminat with CTRL+C in main
        self.thread.start()
        
