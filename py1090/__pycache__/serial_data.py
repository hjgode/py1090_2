# serial class to get noise level
import serial
import threading

class SerialData:
	def __init__(self, p):
		self.noiselevel=60
		self.connected=false
		self.port=p
		self.serialport=serial.Serial(p, 115200, timeout=0)

	def get_noiselevel(self):
		return self.noiselevel
		
	def handle_data(self,data):
		self.noiselevel=data

	def read_from_port(self,ser):
		while not connected:
		#serin = ser.read()
		connected = True

			while True:
			   #print("test")
			   reading = ser.readline().decode()
			   handle_data(reading)	
			   
	def startreading(self):
		thread = threading.Thread(target=self.read_from_port, args=(self.serial_port,))
		thread.start()
		