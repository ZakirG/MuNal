import pyen
import matplotlib.pyplot as plt
import os, sys, string, re
import sqlite3
import read_songs
from collections import defaultdict
import time
import urllib2, urlparse
import json

API_KEY = "GX5WDOWGQL5FJBBVF"
#setting the API key
en = pyen.Pyen("GX5WDOWGQL5FJBBVF")

#Returns dictionary; song names are keys, analysis url's are items.
def url_from_sql(database_file, artist_name):
	db = sqlite3.connect(database_file)
	cursor = db.cursor()
	rv = {}
	song_data = cursor.execute("SELECT song_name,analysis_url,id FROM songs WHERE artist_name LIKE (?); ", ['%' + artist_name + '%'])
	for row in song_data:
		rv[row[0].encode("utf-8")] = [row[1].encode("utf-8"), row[2].encode("utf-8")]
	#cursor.close()
	#db.close()
	return rv

#Section scraping data from analysis urls

#Credit to Anne Rogers, taken from pa1's util.py
def request_response(url):
    prefix = "http://"
    if url[:len(prefix)] != prefix:
        url = prefix + url
    
    '''Open connection to url'''
    try:
        response = urllib2.urlopen(url)
        return response
    except urllib2.URLError:
        return None
    except Exception:
        return None
        
#Credit to Anne Rogers, taken from pa1's util.py
def read_from_response(request):
    try:
        return request.read()
    except Exception:
        print "read failed"
        return -1

#This returns json structure for url
def get_json(url):
	try:
		f = request_response(url)
	except:
		print "Exception at: " + str(url)
		return -1
	if f == None:
		print "Reponse failure at: " + str(url)
		return -1
	r = read_from_response(f) #this is the html of our url
	if r == -1:
		print "Read failure at: " + str(url)
		return -1
	json_dict = json.loads(r)
	return json_dict

#Takes return value of url_from_sql to build a dictionary of dictionaries of song features
def build_json_dict(url_dict):
	json_dict = {}
	counter = 0
	print "Number of tracks processed successfully: ",len(url_dict.keys())
	for song in url_dict.keys():
		if counter > 118:
			time.sleep(60) #crucial to avoid echonest access rate limits; allowed 120 queries per minute
			counter = 0
		url = url_dict[song][0]
		id = url_dict[song][1]
		dict = get_json(url)
		if dict == -1:
			continue
		dict["id"] = id
		json_dict[song] = dict
		counter += 1
	return json_dict

#Adds new sql table, track_info to the command line arg database, populated with output of sift
def sql_fill(dict, database):
	db = sqlite3.connect(database)
	db.text_factory = str
	cursor = db.cursor()
	for song in dict.keys():
		song_name = song
		id = str(dict[song]["id"])
		bars = str(dict[song]["bars"]).encode("utf-8")
		segments = str(dict[song]["segments"]).encode("utf-8")
		beats = str(dict[song]["beats"]).encode("utf-8")
		sections = str(dict[song]["sections"]).encode("utf-8")
		tatums = str(dict[song]["tatums"]).encode("utf-8")
		end_of_fade_in = dict[song]["track"]["end_of_fade_in"]
		start_of_fade_out = dict[song]["track"]["start_of_fade_out"]
		cursor.execute("INSERT INTO track_info VALUES(?,?,?,?,?,?,?,?,?);", (song_name, id, bars, segments, beats, sections, tatums, end_of_fade_in, start_of_fade_out))
	db.commit()
	#cursor.close()
	#db.close()

def main():
	if len(sys.argv) > 2:
		database_file = sys.argv[1]
		artist_name = sys.argv[2]
		url_dict = url_from_sql(database_file, artist_name) #added an extra arg to this function
		json_dict = build_json_dict(url_dict)
		sql_fill(json_dict, database_file)
	else:
		print "Usage: python get_track_info.py <database_file> <artist_name>"
		sys.exit(0)

if __name__ == "__main__":
	main()