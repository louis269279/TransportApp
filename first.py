#!/usr/local/bin/python2

import gtfs_realtime_pb2
import urllib2
import sys
import csv
import collections
import time
from datetime import datetime, timedelta

BUS_STOP_MAP = {}
leaveText = ""
goText = ""

def main():
    global leaveText, goText
    if (len(sys.argv) != 3 or ((sys.argv[2] == 'sydneytrains' or sys.argv[2] == 'buses') == False)):
        print("Error with arguments.")
        sys.exit()

    goText += "Result as at [%s]\n" % datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    leaveText += "Result as at [%s]\n" % datetime.now().strftime('%Y-%m-%d %H:%M:%S') 

    header = None
    f = open('complete_gtfs/stops.txt', 'rb')
    reader = csv.reader(f)
    for row in reader:
        if header == None:
            header = row
        else:
            BUS_STOP_MAP[row[0]] = row[2]

    if (sys.argv[1] == '-t'):
        tripupdate(sys.argv[2])
    elif (sys.argv[1] == '-v'):
        vehiclepos(sys.argv[2])

def vehiclepos(transportType):
    feed = gtfs_realtime_pb2.FeedMessage()
    opener = urllib2.build_opener()
    opener.addheaders = [('Authorization', 'apikey 0s1qgK2KAe2F2PUlZga9Ew1JXbuQ52dbWvQn')]
    response = opener.open('https://api.transport.nsw.gov.au/v1/gtfs/vehiclepos/' + transportType)
    #response = opener.open('https://api.transport.nsw.gov.au/v1/publictransport/timetables/complete/gtfs')

    feed.ParseFromString(response.read())

    #print(response.read())
    # print (feed)
    if (transportType == 'sydneytrains'):
        for entity in feed.entity:
            if (entity.vehicle.trip.route_id == 'AEHL_1a'):
                print(entity)

    elif (transportType == 'buses'):
        for entity in feed.entity:
            if (entity.id.split("_")[3] == '370'):
                print(entity)

def tripupdate(transportType):
    feed = gtfs_realtime_pb2.FeedMessage()
    opener = urllib2.build_opener()
    opener.addheaders = [('Authorization', 'apikey 0s1qgK2KAe2F2PUlZga9Ew1JXbuQ52dbWvQn')]

    start_time = time.time()
    response = opener.open('https://api.transport.nsw.gov.au/v1/gtfs/realtime/' + transportType)
    feed.ParseFromString(response.read())
    print("Time taken to send request and parse response: %s seconds" % (time.time() - start_time))


    if (transportType == 'sydneytrains'):
        for entity in feed.entity:
            if (entity.trip_update.trip.route_id == 'AEHL_1a'):
                print(entity)

    elif (transportType == 'buses'):
        global leaveText, goText
        results = []
        bus_trip_dets = collections.defaultdict(str)
        for entity in feed.entity:
            active = False
            if (entity.id.split("_")[3] == '370'):
                for stop_time_update in entity.trip_update.stop_time_update:
                    bus_trip_dets[entity.id] += "\n[Arrival: " + datetime.fromtimestamp(int(stop_time_update.arrival.time)).strftime('%Y-%m-%d %H:%M:%S') + "] " + (BUS_STOP_MAP[stop_time_update.stop_id])
                    if ((stop_time_update.stop_id == '203114')
                            or (stop_time_update.stop_id == '201715')):

                        now = datetime.now()
                        then = datetime.fromtimestamp(int(stop_time_update.arrival.time))
                        tdelta = then - now
                        #minutes, seconds = divmod(remainder, 60)
                        #print ("Time till next bus: %s minutes %s seconds" % divmod(remainder, 60))
                        results.append((entity.id, tdelta.seconds, stop_time_update.stop_id))
                        active = True
                        #print(datetime.fromtimestamp(int(stop_time_update.arrival.time)).strftime('%Y-%m-%d %H:%M:%S'))
                        #stop_time_update.stop_id += ' ' + BUS_STOP_MAP[stop_time_update.stop_id]
                    
                    elif ((active and stop_time_update.stop_id == '201511')
                            or (active and stop_time_update.stop_id == '203255')):
                        break
                    #print(entity)

        results.sort(key=lambda tup: tup[1])
        for (entity_id, total_seconds, stop_id) in results:
            hours, remainder = divmod(total_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            if stop_id == '203114':
                leaveText += ("Time till next bus: %s hours %s minutes %s seconds" % (hours, minutes, seconds))
                leaveText += (bus_trip_dets[entity_id])
                leaveText += ("\n--------------------\n\n")
            elif stop_id == '201715':
                goText += ("Time till next bus: %s hours %s minutes %s seconds" % (hours, minutes, seconds))
                goText += (bus_trip_dets[entity_id])
                goText += ("\n--------------------\n\n")

    with open("370LeaveUni.txt", "w") as f:
        f.write(leaveText)

    with open("370GoToUni.txt", "w") as f:
        f.write(goText) 

main()
