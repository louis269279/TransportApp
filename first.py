#!/usr/local/bin/python2

import gtfs_realtime_pb2
import urllib2
import sys
import csv

def main():
    if (len(sys.argv) != 3 or ((sys.argv[2] == 'sydneytrains' or sys.argv[2] == 'buses') == False)):
        sys.exit()

    f = open('complete_gtfs/stops.txt', 'rb')
    reader = csv.reader(f)
    stopsMap = {}
    for row in reader:
        if rownum ==0:
            header = row
        else:
            stopsMap[row[0]] = row[2]


    if (sys.argv[1] == '-t'):
        tripupdate(sys.argv[2])
    elif (sys.argv[1] == '-v'):
        vehiclepos(sys.argv[2])

def vehiclepos(type):
    feed = gtfs_realtime_pb2.FeedMessage()
    opener = urllib2.build_opener()
    opener.addheaders = [('Authorization', 'apikey 0s1qgK2KAe2F2PUlZga9Ew1JXbuQ52dbWvQn')]
    response = opener.open('https://api.transport.nsw.gov.au/v1/gtfs/vehiclepos/' + type)
    #response = opener.open('https://api.transport.nsw.gov.au/v1/publictransport/timetables/complete/gtfs')

    feed.ParseFromString(response.read())

    #print(response.read())
    # print (feed)
    if (type == 'sydneytrains'):
        for entity in feed.entity:
            if (entity.vehicle.trip.route_id == 'AEHL_1a'):
                print(entity)

    elif (type == 'buses'):
        for entity in feed.entity:
            if (entity.id.split("_")[3] == '370'):
                print(entity)

def tripupdate(type):
    feed = gtfs_realtime_pb2.FeedMessage()
    opener = urllib2.build_opener()
    opener.addheaders = [('Authorization', 'apikey 0s1qgK2KAe2F2PUlZga9Ew1JXbuQ52dbWvQn')]
    response = opener.open('https://api.transport.nsw.gov.au/v1/gtfs/realtime/' + type)
    feed.ParseFromString(response.read())

    if (type == 'sydneytrains'):
        for entity in feed.entity:
            if (entity.trip_update.trip.route_id == 'AEHL_1a'):
                print(entity)

    elif (type == 'buses'):
        for entity in feed.entity:
            if (entity.id.split("_")[3] == '370'):
                print(entity)

main()