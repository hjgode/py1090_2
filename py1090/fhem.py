#modul fhem.py
import telnetlib

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
	
def senddata(flight, viewdistance, noise):
	print("senddata: ", flight, viewdistance, noise)
	tn=telnetlib.Telnet("atom2", 7072, 3)
	#tn.read_until("is '^]'.".encode(),2)
	#tn.read_all()
	tn.write("\n".encode())
	tn.read_until("fhem> ".encode(),2)
	
	#send data now
	data="setreading fluglaerm distance "+strformat(viewdistance)+ "; setreading fluglaerm callsign "+flight+"; setreading fluglaerm noise "+strformat(noise)+";"
	tn.write(data.encode())	
	tn.read_until("fhem> ".encode(),2)
	
	tn.write("exit\n".encode())
	print (tn.read_all())
	tn.close()
	print("senddata done.")
	return
	