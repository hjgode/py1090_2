from py1090.display import display
from py1090.message import *
from py1090.collection import *
from curses import wrapper

import time

def main(screen):
	disp = display(screen)
	collection=FlightCollection()
	file=open("./message.log", "r")
	for i in range (0,500):
		line=file.readline()
		disp.add_line(line)
		time.sleep(0.1)
	#print(line)
	file.close()
	time.sleep(5)
	
if __name__ == "__main__":
	wrapper(main)	
