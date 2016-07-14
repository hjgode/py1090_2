#!/usr/bin/env python3
import json
from urllib.request import urlopen

#nodemcu v2 running espeasy
nodemcu='http://192.168.0.70/json'

def getdata():
	print("getdata: ...")
	noise=0
	try:
		with urlopen(nodemcu) as r:
   			result = json.loads(r.read().decode(r.headers.get_content_charset('utf-8')))
		#print(result, "\n=================")
		noise=result['Sensors'][0]["Analog"]
		#print ("noise: ", noise)
		print ("noise int: ", int(noise*1024/1000*3/10))
		noise=int(noise*1024/1000*3/10)
	except:
		print("exception json read")
	print("getdata done.")
	return noise;

print (getdata())