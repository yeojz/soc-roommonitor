import urllib2
import Queue
import threading
import datetime
import json
from bs4 import BeautifulSoup

#	Structure of json output: output -> Array of Rooms -> Dict of room, bookings
#	bookings -> Dict of purpose, time

baseURL = "https://mysoc.nus.edu.sg/~calendar/getBooking.cgi?room=%s&thedate=%s"
sampleRoomName = 'DR1'

# Get all rooms name
def getAllRoomsName():
	html = urllib2.urlopen(baseURL).read()
	soup =  BeautifulSoup(''.join(html))
	options = soup.findAll('option')
	rooms = []
	options.pop(0)
	for option in options:
		rooms.append(option['value'])
	
	return rooms

# Return today in the from of YYYY-MM-DD
def getToday():
	return str(datetime.date.today()).replace("-","/")
	
# Convert time from 12:00am to 0000
def convertHours(hourString):
	if len(hourString) == 6:
		hourString = '0'+hourString
	if 'pm' in hourString and hourString != '12:00pm':
		return str(int(hourString[0:2]) + 12) + hourString[3:5]
	else:
		if hourString != '12:00am':
			hour = str(int(hourString[0:2])) + hourString[3:5]
			if len(hour) == 3:
				hour = '0'+hour
			return hour
		else:
			return '0000'
	
	
# Returns an object representation of the room's schedule
def getRoomDayBooking(room,day):
	roomSchedule = {}
	roomSchedule['room'] = room
	targetURL = baseURL % (room,day)
	html = urllib2.urlopen(targetURL).read()
	soup =  BeautifulSoup(''.join(html))
	bookings = soup.findAll('tr')
	slots = []
	if len(bookings) > 0 and bookings[0].get_text() != "No bookings made.":
		for booking in bookings:
			slot = {}
			time_str = str(booking.contents[0])
			purpose_str = str(booking.contents[1])
			time = time_str[4:len(time_str)-5].split(' - ')

			try:
				slot['starttime'] = convertHours(time[0])
			except:
				pass
			try:
				slot['endtime'] = convertHours(time[1])
			except:
				pass
							
			#slot['starttime'] = time_str[4:len(time_str)-5]
			slot['purpose'] = purpose_str[4:len(purpose_str)-5]
			slots.append((slot))
		
	roomSchedule['bookings'] = slots
	return roomSchedule
	
# Stores room schedules in a queue
def storeRoomDayBooking(room,day,q):
	q.put(getRoomDayBooking(room,day))
	
# Create threads and crawl room schedule for each room
def getRoomsTodayBooking(rooms):
	socRoomsTodayBooking = []
	roomThreads = []
	q = Queue.Queue()
	for room in rooms:
		t = threading.Thread(target=storeRoomDayBooking, args=(room, getToday(), q))
		t.daemon = True
		t.start()
		roomThreads.append(t)
	
	for t in roomThreads:
		t.join()
		if not q.empty():
			socRoomsTodayBooking.append(q.get())
			
	return socRoomsTodayBooking
	
# Get all rooms schedule available
def getAllRoomsTodayBooking():
	return getRoomsTodayBooking(getAllRoomsName())
	
# Method to dump result as a file
def dumpAllRoomsTodayBookingToFile(fileName):
	outputFile = open(fileName, 'w')
	outputFile.write(json.dumps(getAllRoomsTodayBooking()))
	
