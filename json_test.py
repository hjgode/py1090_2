import requests

r = requests.get('http://192.168.0.70/json')
jdata=r.json()
print (jdata)
print ("Status: ", r.status_code)
print ("noise: ", jdata['Sensors'][0]["Analog"])

