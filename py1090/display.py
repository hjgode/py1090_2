#from .ansi import Terminal
import curses
#from curses import wrapper
from .message import *
from .collection import *
import datetime

"""
date      |time    |msgcount|num flights|
------------------------------------------------------------------------------
ICOA      |call sign |lat   |lon   |dist |view |last seen |
------------------------------------------------------------------------------
hexi1...
hexi2...

write_head

display_flight (need hex to identify col starting at 4) 
	update col if exists
	remove col and then move up rest
	add col or insert col
	maintain flights in internal list/dict/array
"""
class display:
	
	def __init__(self,screen):
		self.CLEANUP_TIMEOUT=5 #minutes a flight has to be last seen before cleanup
		self.date="2016-01-01"
		self.time="00:00:00"
		self.nearest=None #store nearest flight
		self.nearest_row=0
		self.left_offs=0
		self.msg_cnt=0
		self.num_flights=0
		self.collection=FlightCollection()
		self.term=screen
		#self.term.clear()
		self.write_head()

	def cleanup(self, _flightcollection, _record_time):
		"""find flights which last_seen older than 5 minutes and clean this
		returns Nothing
		"""
		toremove=[]
		for f in _flightcollection:
			if f.last_seen:
	       		#print("last_seen: ", f.last_seen, datetime.datetime.now())
				tdiff=_record_time - f.last_seen
				if tdiff > datetime.timedelta(minutes=self.CLEANUP_TIMEOUT):
					#print("---- remove: ", f.hexident)
					toremove.append(f.hexident)
		for i in toremove:
			_flightcollection.remove(i)
		return
		
	def write_head(self):
		#clear top line
		row=1
		col=self.left_offs
		#                         0          1         2          3          4         5         6         7            
		#                         date      |time    |msgcount|num flights|
		self.term.addstr(row,col,"          |        |        |           |                                     ")
		row+=1
		self.term.addstr(row,col,"------------------------------------------------------------------------------")
		row+=1
		self.term.addstr(row,col,"ICOA      |call sign |lat   |lon   |dist |view |alt   |last seen |")
		row+=1
		self.term.addstr(row,col,"------------------------------------------------------------------------------")
		self.term.refresh()

	def update_timestamp(self,timestamp):
		row=1
		sDate=timestamp.strftime('%Y-%m-%d')
		sTime=timestamp.strftime('%H:%M:%S')
		col=self.left_offs+0
		self.term.addstr(row,col,sDate)
		col=self.left_offs+11
		self.term.addstr(row,col,sTime)

	def update_head(self):
		row=1
		#timestamp=datetime.datetime.now()
		#self.update_timestamp(timestamp)
		
		#show num of msg processed
		col=self.left_offs+21
		self.term.addstr(row,col, "{0:>6}".format(self.msg_cnt))
		
		#show current num of flights
		col=self.left_offs+34
		self.term.addstr(row,col,"{:02d}".format(len(self.collection)))
		
		self.term.refresh()
		
	def add_line(self, line):
		msg=Message.from_string(line)
		timestamp=msg.generation_time
		self.update_timestamp(timestamp)
		
		#show num of msg processed
		self.msg_cnt+=1
		self.term.addstr(1,self.left_offs+21, "{0:>6}".format(self.msg_cnt))
		
		#cleanup collection for disapeared flights
		if msg.record_time:
			self.cleanup(self.collection, msg.record_time)
		
		self.collection.add(msg)
		#get data from filghtcolletion and update screen
		self.update_head()
		self.print_coll()
		self.term.refresh()
		
	def print_coll(self):
		#print flights line by line
		row=5
		self.nearest=None
		self.nearest_row=0
		col=self.left_offs
		for flight in self.collection:
			self.print_flight(flight,row)
			row+=1
		#make nearest flight line bold
		if self.nearest_row!=0:
			self.term.chgat(self.nearest_row, self.left_offs, curses.A_BOLD)
			

	def print_flight(self,flight,row):
		#print flight details line
		col=self.left_offs
		self.term.addstr(row,col,"{0:>8}".format(flight.hexident))
		
		col=self.left_offs+11
		self.term.addstr(row,col,flight.callsign);
		
		(lat,lon)=flight.last_position
		if lat != None:
			col=self.left_offs+22
			self.term.addstr(row,col,"{0:02.3f}".format(lat))
		if lon != None:
			col=self.left_offs+30
			self.term.addstr(row,col,"{0:02.3f}".format(lon))
			
		lastdist=flight.last_distance
		if lastdist!=None:
			col=self.left_offs+36
			self.term.addstr(row,col,"{0:02.1f}".format(lastdist))
		
		#view distance
		lastview=flight.abs_distance
		if lastview!=None and lastview!=100000:
			col=self.left_offs+42
			self.term.addstr(row,col,"{0:02.1f}".format(lastview))
			if self.nearest==None:
				self.nearest_row=row
				self.nearest=lastview
			elif self.nearest>lastview:
				self.nearest=lastview
				self.nearest_row=row
		
		lastalt=flight.last_altitude
		if lastalt!=None:
			col=self.left_offs+50
			self.term.addstr(row,col,"{0:02.1f}".format(lastalt*0.3048 / 1000)) #feets and km
			
		lastseen=flight.last_seen
		if lastseen!=None:
			col=self.left_offs+55
			self.term.addstr(row,col,lastseen.strftime('%H:%M:%S'))
		
		self.term.clrtobot()

		self.term.clrtobot()
		