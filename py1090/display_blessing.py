#from .ansi import Terminal
from blessings import *
#import curses
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

	#TODO implement a callback that can be called for printing status messages
	def __init__(self,screen):
		self.CLEANUP_TIMEOUT=5 #minutes a flight has to be last seen before cleanup
		self.date="2016-01-01"
		self.time="00:00:00"
		self.nearest=None #store nearest flight view distance
		self.nearest_row=0
		self.nearest_flight=None
		self.left_offs=0
		self.top_offs=0
		self.msg_cnt=0
		self.num_flights=0
		self.collection=FlightCollection()
		self.term=Terminal()
		self.term.fullscreen()
		self.term.clear()
#		self.height=self.term.height
#		self.width = self.term.width
		self.cleartobot(0)
		self.write_head()

	@property
	def height(self):
		return self.term.height
	@property
	def width (self):
		return self.term.width
			
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
		
	def myaddstr(self, r,c,txt):
		w=self.term.width
		h=self.term.height
		#if curses.is_term_resized(h, w):
		#	self.height, self.width= self.term.getmaxyx()
		#	self.term.clear()
		#	curses.resizeterm(self.height, self.width)
		#self.write_head()
		#self.term.refresh()
		#slice first part until screen width is reached
		# if len(str)>self.width-c 
		if len(txt) > self.width-c:
			t=txt[:self.width-c]
		else:
			t=txt
		try:
			with self.term.location(self.left_offs, self.term.height-1):
				print (self.term.move(r,c) + t, end='\r') #end='\r' needed to avoid scrolling
#			print (self.term.move(r,c) + t)
#			self.term.addstr(r,c,t)
		except:
			return
			
	def write_head(self):
		#clear top line
		row=self.top_offs
		col=self.left_offs
		#                         0          1         2          3          4         5         6         7            
		#                         date      |time    |msgcount|num flights|
		self.myaddstr(row,col,"          |        |        |           |                                     ")
		row+=1
		self.myaddstr(row,col,"---------------------------------------------------------------------------------")
		row+=1
		self.myaddstr(row,col,"ICOA      |call sign |lat   |lon   |dist |view |alt   |last seen |noise |g_speed|")
		row+=1
		self.myaddstr(row,col,"---------------------------------------------------------------------------------")
#		self.term.refresh()

	def update_timestamp(self,timestamp):
		row=self.top_offs
		sDate=timestamp.strftime('%Y-%m-%d')
		sTime=timestamp.strftime('%H:%M:%S')
		col=self.left_offs+0
		self.myaddstr(row,col,sDate)
		col=self.left_offs+11
		self.myaddstr(row,col,sTime)

	def update_head(self):
		row=self.top_offs
		#timestamp=datetime.datetime.now()
		#self.update_timestamp(timestamp)
		
		#show num of msg processed, now in addline
#		col=self.left_offs+21
#		self.myaddstr(row,col, "{0:>6}".format(self.msg_cnt))
		
		#show current num of flights
		col=self.left_offs+34
		self.myaddstr(row,col,"{:02d}".format(len(self.collection)))
		
#		self.term.refresh()
		
	def add_line(self, line):
		msg=Message.from_string(line)
		timestamp=msg.generation_time

		self.write_head()
		self.update_head()
		self.update_timestamp(timestamp)
		
		#show num of msg processed
		self.msg_cnt+=1
		self.myaddstr(self.top_offs, self.left_offs+21, "{0:>6}".format(self.msg_cnt))
		
		#cleanup collection for disapeared flights
		if msg.record_time:
			self.cleanup(self.collection, msg.record_time)
		
		self.collection.add(msg)
		#get data from filghtcolletion and update screen
#		self.update_head()
		self.print_coll()
#		self.term.refresh()
		
	def set_coll(self,coll, timestamp):
		self.collection=coll
#		self.update_timestamp(timestamp)
		
		#show num of msg processed
		self.msg_cnt+=1
		self.myaddstr(self.top_offs,self.left_offs+21, "{0:>6}".format(self.msg_cnt))
		
		self.write_head()
		self.update_head()
		self.update_timestamp(timestamp)
		
		self.print_coll()
		self.update_timestamp(timestamp)
#		self.term.refresh()
		
	def print_coll(self):
		#print flights line by line
		row=self.top_offs+4
		self.nearest=100000
		self.nearest_row=0
		self.nearest_flight=None
		col=self.left_offs
		for flight in self.collection:
#			self.term.chgat(col, row, curses.A_NORMAL)
			self.print_flight(flight,row)
			row+=1
		#curses.doupdate()
		self.cleartobot(row)
		#make nearest flight line bold or makr other way
		if self.nearest_flight!=None:
			print (self.term.move(self.nearest_row, self.left_offs) + self.term.bold + "x" + self.term.normal, end='\r')
#			self.print_flight(self.nearest_flight, self.nearest_row)
#			print (self.term.move(self.nearest_row, self.left_offs) + self.term.normal)
#			self.term.chgat(self.nearest_row, self.left_offs, curses.A_BOLD)
			
	def print_msg(self,txt):
		"""
		self.term.addstr(5,1,"size: {0} / {1}".format(self.height, self.width))
		self.term.addstr(6,1,txt)
		self.term.refresh()
		"""
		row=self.height-2
		col=self.left_offs
		#self.term.addstr(7,1,"addstr row,col: {0} / {1}".format(row, col))
		#self.term.getch()
		self.myaddstr(row, col, txt)

	def cleartobot(self,current_row):
		blanks=" " * (self.width - self.left_offs)
#		self.myaddstr(current_row, self.left_offs, blanks)
#		self.term.move(current_row+1,self.left_offs) 
#		self.term.clear_eos()

		for i in range(current_row, self.height-2):
#			print (self.term.moveto(i,self.left_offs) + "                                                          "
#			curses.setsyx(i, self.left_offs)
#			self.term.clrtoeol()
			self.myaddstr(i, self.left_offs, blanks)
			
	def print_flight(self,flight,row):
		if row>=self.height-4:
			return
		#clear line
		blanks=" " * (self.width - self.left_offs)
		self.myaddstr(row,self.left_offs,blanks)
		
		#self.term.attron(curses.A_NORMAL)
		#print flight details line
		col=self.left_offs
		self.myaddstr(row,col,"{0:>8}".format(flight.hexident))
		
		col=self.left_offs+11
		self.myaddstr(row,col,flight.callsign);
		
		(lat,lon)=flight.last_position
		if lat != None:
			col=self.left_offs+22
			self.myaddstr(row,col,"{0:02.3f}".format(lat))
		if lon != None:
			col=self.left_offs+30
			self.myaddstr(row,col,"{0:02.3f}".format(lon))
			
		lastdist=flight.last_distance
		if lastdist!=None:
			col=self.left_offs+36
			self.myaddstr(row,col,"{0:02.1f}".format(lastdist))
		
		#view distance
		lastview=flight.abs_distance
		if lastview!=None and lastview!=100000:
			col=self.left_offs+42
			self.myaddstr(row,col,"{0:02.1f}".format(lastview))
			if lastview < self.nearest:
				self.nearest=lastview
				self.nearest_row=row
				self.nearest_flight=flight
		
		lastalt=flight.last_altitude
		if lastalt!=None:
			col=self.left_offs+50
			# :0 leading zero
			# :>04.1f leading zero, 4 places over all, including the dot and one digit after dot, right aligned
			self.myaddstr(row,col,"{0:>04.1f}".format(lastalt*0.3048 / 1000)) #feets and km
			
		lastseen=flight.last_seen
		if lastseen!=None:
			col=self.left_offs+56
			self.myaddstr(row,col,lastseen.strftime('%H:%M:%S'))
		
		noise=flight.noise
		if noise!=None:
			col=self.left_offs+67
			self.myaddstr(row,col,"{0:>4}".format(noise))

		groundspeed=flight.min_ground_speed
		if groundspeed!=None:
			col=self.left_offs+75
			self.myaddstr(row,col,"{0:>4.0f}".format(groundspeed))

#		self.term.clrtobot()
		