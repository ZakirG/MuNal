# ##################################################
# This script takes a text file list of songs as input
# Uses echonest to find information on all these songs and make an SQLite database, referenced in a command line arg
# Usage: python read_songs.py <text file of songs> <database>
# Example: python read_songs.py song_lists/list_of_songs.txt song_database.db
# ##################################################
import pyen
import matplotlib.pyplot as plt
import sys, string, re
import sqlite3

API_KEY = "GX5WDOWGQL5FJBBVF"
#setting the API key
en = pyen.Pyen("GX5WDOWGQL5FJBBVF")

def song_search(combined_input,result_num=0):
	"""Returns song id"""
	response = en.get('song/search', api_key=API_KEY, combined=combined_input)
	if result_num >= len(response["songs"]):
		return -1
	return response["songs"][result_num]["id"]

def song_profile(combined_input, result_num=0):
	"""Returns song profile, an EchoNest construct, in dictionary form"""
	id = song_search(combined_input, result_num)
	if id == -1:
		return -1
	response = en.get('song/profile', api_key=API_KEY, id=id, bucket="audio_summary")
	return response["songs"][result_num]

def get_name(song_profile):
	return str(song_profile["title"])

def get_bpm(song_profile):
	return song_profile["audio_summary"]["tempo"]

def get_time_sig(song_profile):
	return song_profile["audio_summary"]["time_signature"]

def get_key(song_profile):
	return song_profile["audio_summary"]["key"]
	
def get_duration(song_profile):
	return song_profile["audio_summary"]["duration"]

def get_speechiness(song_profile):
	return song_profile["audio_summary"]["speechiness"]

def get_loudness(song_profile):
	return song_profile["audio_summary"]["loudness"]

def read_songs(filename):
	"""Reads and cleans song names from file to create a dictionary"""
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
		print "\t" + song_name
		profile = song_profile(song_name)
		#If song is not found in echonest database:
		if profile == -1:
			total_songs += 1
			print "Not processed."
			continue
		print "Processed as: " + get_name(profile)
		num_successful += 1
		total_songs += 1
		song_list[get_name(profile)] = profile
	print str(num_successful) + " successful out of " + str(total_songs)
	return song_list #a dictionary

def main():
	print song_profile("tom ford jay-z")
	#print "Tom Ford: " + str(get_bpm(song_profile("tom ford jay-z")))
	#print "Tuscan Leather: " + str(get_bpm(song_profile("tuscan leather drake")))
	if len(sys.argv) > 1:
		filepath = sys.argv[1]
		r = read_songs(filepath)		
		#Create SQL database
		database_name = sys.argv[2]
		db = sqlite3.connect(database_name)
		cursor = db.cursor()
		#cursor.execute("CREATE TABLE songs(song_name TEXT, bpm decimal(10,10), time_sig INTEGER, key INTEGER, id TEXT, duration decimal(10,10), speechiness decimal(10,10), loudness decimal(10,10), song_profile TEXT);")
		for song in r.keys():
			print song
			sp = r[song]
			cursor.execute("INSERT INTO songs VALUES(?,?,?,?,?,?,?,?,?,?,?);", (sp["title"],sp["artist_name"], get_bpm(sp), get_time_sig(sp), get_key(sp), sp["id"], sp["analysis_url"], get_duration(sp), get_speechiness(sp), get_loudness(sp), str(sp)))
		db.commit()
		
	else:
		print "Usage: python read_songs.py <text file of songs> <database>"

if __name__ == "__main__":
	main()
