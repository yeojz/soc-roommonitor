from flask import Flask
from flask import request
from flask import Response
import SocRoomScheduleCrawler
import NusRoomScheduleCrawler
import json
app = Flask(__name__)

@app.route('/room/')
def hello_world():
    return 'Hello World!'

@app.route('/room/getschedule.json')
def getschedule():
    if 'rooms' in request.args:
        rooms = str(request.args['rooms']).upper()
    else:
        results = 'Specific rooms parameter (Comma separated). Remember to change / to %2F'
        return Response(json.dumps(results), status=400, mimetype='application/json')

    rooms = rooms.split(',')
    socRoomsName = SocRoomScheduleCrawler.getAllRoomsName()
    forSocCrawler = []
    forNusCrawler = []

    for room in rooms:
        if room in socRoomsName:
            forSocCrawler.append(room)
        else:
            forNusCrawler.append(room)
    try:
        results = SocRoomScheduleCrawler.getRoomsTodayBooking(forSocCrawler)
    except:
        pass
    try:
        results += NusRoomScheduleCrawler.getRoomsTodayBooking(forNusCrawler)
    except:
        pass
    return Response(json.dumps(results), status=200, mimetype='application/json')

if __name__ == '__main__':
    app.run()

