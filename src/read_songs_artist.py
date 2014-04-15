import pyen
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sys, string, re
import sqlite3
from time import sleep
import read_songs as rs
#short tutorial here https://github.com/plamere/pyen
#API overview here http://developer.echonest.com/docs/v4/song.html#profile
#This script take a text file list of songs by one artist as input, and an artist name
#Uses echonest to find information on all these songs and modify an SQLite database, referenced in a command line arg
#Usage: python read_songs_artist.py <text file of songs> <database> <artist name>
#example: python read_songs_artist.py song_lists/kanye_west.txt genre_db/rap.db Kanye\ West


API_KEY = "GX5WDOWGQL5FJBBVF"
#setting the API key
en = pyen.Pyen("GX5WDOWGQL5FJBBVF")

#original implentation, searches by song name, return song id
def song_search(combined_input,result_num=0, api_key=API_KEY):
	response = en.get('song/search', api_key=API_KEY, combined=combined_input)
	if result_num >= len(response["songs"]):
		return -1
	return response["songs"][result_num]["id"]

#newer version, searches by song name and artist, return song id
def song_search_artist(song_name, artist_input,result_num=0):
	response = en.get('song/search', api_key=API_KEY, title=song_name, artist=artist_input)
	if result_num >= len(response["songs"]):
		return -1
	return response["songs"][result_num]["id"]

#return dictionary of basic song info
def song_profile(named_input, artist, result_num=0):
	if artist == -1:
		id = song_search(named_input, result_num)
	else:
		id = song_search_artist(named_input, artist, result_num)
	if id == -1:
		return -1
	response = en.get('song/profile', api_key=API_KEY, id=id, bucket="audio_summary")
	return response["songs"][result_num]
	
#made reading a function so that we only open each file for reading *once*
def read_songs(filename, artist=-1):
	f = open(filename, 'r')
	z = f.read()
	f.close()
	z = z.split("\n")
	z = [song for song in z if len(song) > 1]
	song_list = {}
	#excluding all punctuation, except for dashes (we care about jay-z)
	exclude = string.punctuation
	#exclude = exclude.translate(string.maketrans("",""), "-")
	num_successful = 0
	total_songs = 0
	for song in z:
		song_name = song #.encode('utf-8')
		if "/" in song_name:
			s = [c for c in song]
			while "/" in s:
				tmpnum = s.index("/")
				s = s[(tmpnum + 1):]
			song_name = "".join(s)
		#Remove .mp3 extension
		if song_name[-1] == "3" or song_name[-2]=="4":
			song_name = song_name[0:-4]
		if "ft." in song_name.lower():
			cutoff = string.find(song_name.lower(), "ft.")
			if cutoff != -1:
				song_name = song_name[0:cutoff]
		if "feat" in song_name.lower():
			cutoff = string.find(song_name.lower(), "feat")
			if cutoff != -1:
				song_name = song_name[0:cutoff]
		if "featuring" in song_name.lower():
			cutoff = string.find(song_name.lower(), "featuring")
			if cutoff != -1:
				song_name = song_name[0:cutoff]
		song_name = song_name.translate(string.maketrans("",""), exclude)
		exclude2 = "0123456789"
		song_name = song_name.translate(string.maketrans("",""), exclude2)
		#case-insensitively remove the phrase "Lyrics"
		if "lyrics" in song_name.lower():
			song_name = re.sub("(?i)lyrics", "", song_name)
		if "explicit" in song_name.lower():
			song_name = re.sub("(?i)explicit", "", song_name)
		if artist.lower() in song_name.lower():
			song_name = re.sub("(?i)"+artist, "", song_name)
		print "\t" + song_name
		profile = song_profile(song_name, artist)
		#If song is not found in echonest database:
		if profile == -1:
			total_songs += 1
			print "Not processed."
			continue
		print "Processed as: " + rs.get_name(profile)
		num_successful += 1
		total_songs += 1
		song_list[rs.get_name(profile)] = profile
	print str(num_successful) + " successful out of " + str(total_songs)
	return song_list #a dictionary

def main():
	if len(sys.argv) > 3:
		filepath = sys.argv[1]
		database_name = sys.argv[2]
		artist = str(sys.argv[3])
		r = read_songs(filepath,artist)		
		#Create SQL database
		db = sqlite3.connect(database_name)
		cursor = db.cursor()
		print song
		sp = r[song]
		cursor.execute("INSERT INTO songs VALUES(?,?,?,?,?,?,?,?,?,?,?);", (sp["title"],sp["artist_name"], rs.get_bpm(sp), rs.get_time_sig(sp), rs.get_key(sp), sp["id"], sp["analysis_url"], rs.get_duration(sp), rs.get_speechiness(sp), rs.get_loudness(sp), buffer(str(sp)) ))
		db.commit()
		
	else:
		print "Usage: python read_songs_artist.py <text file of songs> <database> <artist name>"

if __name__ == "__main__":
	main()
