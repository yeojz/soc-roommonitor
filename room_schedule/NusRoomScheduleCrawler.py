import urllib2
import Queue
import threading
import datetime
import json
from bs4 import BeautifulSoup

#	Structure of json output: output -> Array of Rooms -> Dict of room, bookings
#	bookings -> Dict of purpose, time

baseURL = "http://137.132.5.219:8000/reporting/individual;Locations;name;%s?template=SWSCUST+Location+Individual&weeks=&days=%s&periods=&Width=0&Height=0"
sampleRoomName = 'COM1-0212'

# Return today in the from of YYYY-MM-DD
def getTodayWeekday():
	return datetime.date.today().weekday()+1
	
# Convert hours from 1:00 to 0100
def convertHours(hours):
	if len(hours) == 4:
		return '0' +hours[0:1] + hours[2:4]
	else:
		return hours[0:2] + hours[3:5]
				
	
# Returns an object representation of the room's schedule
def getRoomDayBooking(room,dayOfWeek):
	roomSchedule = {}
	roomSchedule['room'] = room
	targetURL = baseURL % (room,dayOfWeek)
	print targetURL
	try:
		html = urllib2.urlopen(targetURL).read()
	except:
		roomSchedule['bookings'] = []
		return roomSchedule
		
	soup =  BeautifulSoup(''.join(html))
	bookings = soup.findAll('td', colspan="1")
	
	slots = []
	for booking in bookings:
		data = booking.findAll('td', bgcolor="#FFFFFF")
		if len(data) == 0:
			continue
		
		info = []
		for d in data:
			d = d.findAll(text=True)
			if d:
				info.append(d[0])
		
		slot = {}
		slot['purpose'] = info[0]
		if len(info) > 3:
			slot['purpose'] += '<br>' + info[3]
		
		slot['starttime'] = convertHours(info[1])
		slot['endtime'] = convertHours(info[2])
		slots.append(slot)
			
	roomSchedule['bookings'] = slots
	return roomSchedule
	
# Stores room schedules in a queue
def storeRoomDayBooking(room,day,q):
	q.put(getRoomDayBooking(room,day))
	
# Create threads and crawl room schedule for each room
def getRoomsTodayBooking(rooms):
	nusRoomsTodayBooking = []
	roomThreads = []
	q = Queue.Queue()
	for room in rooms:
		t = threading.Thread(target=storeRoomDayBooking, args=(room, getTodayWeekday(), q))
		t.daemon = True
		t.start()
		roomThreads.append(t)
	
	for t in roomThreads:
		t.join()
		if not q.empty():
			nusRoomsTodayBooking.append(q.get())
			
	return nusRoomsTodayBooking

