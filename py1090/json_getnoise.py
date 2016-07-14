#!/usr/bin/env python3
import json
import threading
from urllib.request import urlopen

#nodemcu v2 running espeasy
nodemcu='http://192.168.0.70/json'

class json_noise:
	def __init__(self, callback):
		self.is_alive=True
		self._noise=0
		self.thread=None
		self.startreading()
		self._callback=callback
	
	def print_msg(self,txt):
		self._callback(txt);
		
	def get_noise(self):
		return self._noise
		
	def getdata(self):
	#	print("getdata: ...")
		n=0
		try:
			while self.is_alive:
				with urlopen(nodemcu) as r:
					result = json.loads(r.read().decode(r.headers.get_content_charset('utf-8')))
					#print(result, "\n=================")
					noise=result['Sensors'][0]["Analog"]
					#print ("noise: ", noise)
			#		print ("noise int: ", int(noise*1024/1000*3/10))
					n=int(noise*1024/1000*3/10)
					self._noise=n
					self.print_msg("noise; {0}".format(n))
		except:
			self.print_msg("exception json read")
	#	print("getdata done.")
		return;

	def startreading(self):
		self.thread = threading.Thread(target=self.getdata)
		self.thread.daemon=True # let's terminat with CTRL+C in main
		self.thread.start()
