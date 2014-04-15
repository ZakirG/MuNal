import pyen
import matplotlib.pyplot as plt
import sys, string, re
import sqlite3
import read_songs as rs
#This script takes an artist and returns a database with attributes of songs by that artist
#Example: python song_query.py Mozart mozart.db

API_KEY = "GX5WDOWGQL5FJBBVF"
#setting the API key
en = pyen.Pyen("GX5WDOWGQL5FJBBVF")

def artist_search(artist, style, n=100):
	response = en.get('song/search', api_key=API_KEY, artist=artist, results=n)
	return response
	
def main():
	if len(sys.argv) >= 3:
		artist = sys.argv[1]
		database = sys.argv[2]
		#Number of songs to be processed
		if len(sys.argv) >= 4:
			n = sys.argv[3]
		else:
			n = 100
		style = ""
		db = sqlite3.connect(database)
		cursor = db.cursor()
		rv = artist_search(artist, style, n)
		for song in rv["songs"]:
			id = song["id"]
			response = en.get('song/profile', api_key=API_KEY, id=id, bucket="audio_summary")
			sp = response["songs"][0]
			cursor.execute("INSERT INTO songs VALUES(?,?,?,?,?,?,?,?,?,?,?);", (sp["title"], sp["artist_name"], rs.get_bpm(sp), rs.get_time_sig(sp), rs.get_key(sp), sp["id"], sp["audio_summary"]["analysis_url"], rs.get_duration(sp), rs.get_speechiness(sp), rs.get_loudness(sp), "null"))
		db.commit()
		cursor.close()
		db.close()
	else:
		print "Usage: python song_query.py <artist name> <output database file> <number of songs to process>"
		sys.exit(0)

if __name__ == "__main__":
	main()