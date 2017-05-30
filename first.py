#!/usr/local/bin/python2

import gtfs_realtime_pb2
import urllib2
import sys
import csv
from datetime import datetime, timedelta

BUS_STOP_MAP = {}
def main():
    if (len(sys.argv) != 4 or ((sys.argv[2] == 'sydneytrains' or sys.argv[2] == 'buses') == False)):
        sys.exit()

    print("[%s] Application Started." % datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    header = None
    f = open('complete_gtfs/stops.txt', 'rb')
    reader = csv.reader(f)
    for row in reader:
        if header == None:
            header = row
        else:
            BUS_STOP_MAP[row[0]] = row[2]

    if (sys.argv[1] == '-t'):
        tripupdate(sys.argv[2], sys.argv[3])
    elif (sys.argv[1] == '-v'):
        vehiclepos(sys.argv[2], sys.argv[3])

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

def tripupdate(transportType, travelDirection):
    feed = gtfs_realtime_pb2.FeedMessage()
    opener = urllib2.build_opener()
    opener.addheaders = [('Authorization', 'apikey 0s1qgK2KAe2F2PUlZga9Ew1JXbuQ52dbWvQn')]
    response = opener.open('https://api.transport.nsw.gov.au/v1/gtfs/realtime/' + transportType)
    feed.ParseFromString(response.read())

    if (transportType == 'sydneytrains'):
        for entity in feed.entity:
            if (entity.trip_update.trip.route_id == 'AEHL_1a'):
                print(entity)

    elif (transportType == 'buses'):
        results = []
        for entity in feed.entity:
            if (entity.id.split("_")[3] == '370'):
                for stop_time_update in entity.trip_update.stop_time_update:
                    if (stop_time_update.stop_id == '203114'):

                        now = datetime.now()
                        then = datetime.fromtimestamp(int(stop_time_update.arrival.time))
                        tdelta = then - now
                        hours, remainder = divmod(tdelta.seconds, 3600)
                        #minutes, seconds = divmod(remainder, 60)
                        #seconds = tdelta.total_seconds()
                        #print ("Time till next bus: %s minutes %s seconds" % divmod(remainder, 60))
                        results.append(remainder)
                        #print(datetime.fromtimestamp(int(stop_time_update.arrival.time)).strftime('%Y-%m-%d %H:%M:%S'))
                        #stop_time_update.stop_id += ' ' + BUS_STOP_MAP[stop_time_update.stop_id]
                    #print(entity)

        results.sort()
        for remainder in results:
            print ("Time till next bus: %s minutes %s seconds" % divmod(remainder, 60))

main()