import pyen
import matplotlib.pyplot as plt
import os, sys, string, re
import sqlite3
import json

#This file will create test statistics from the new data in track_info (but going to retrieve from merged_table)

#Retrieves information from two tables: songs and track_info
#Returns a large dictionary; song keys map to dictionaries of attributes
def merge_retrieve(database_file):
	print "Retrieving information from merged_table;"
	db = sqlite3.connect(database_file)
	cursor = db.cursor()
	rv = {}
	song_data = cursor.execute("SELECT \
		song_name,speechiness,bpm,key,duration,loudness,id,bars,segments,beats,sections,tatums,end_of_fade_in,start_of_fade_out \
		 FROM merged_table;")
	for row in song_data:
		song = {}
		song["song_name"] = row[0].encode("utf-8")
		song["speechiness"] = row[1]
		song["bpm"] = row[2]
		song["key"] = row[3]
		song["duration"] = row[4]
		song["loudness"] = row[5]
		song["id"] = row[6] #.encode("utf-8")
		song["bars"] = row[7].encode("utf-8")
		song["segments"] = row[8].encode("utf-8")
		song["beats"] = row[9].encode("utf-8")
		song["sections"] = row[10].encode("utf-8")
		song["tatums"] = row[11].encode("utf-8")
		song["end_of_fade_in"] = row[12]
		song["start_of_fade_out"] = row[13]
		rv[row[0].encode('utf-8')] = song
	#cursor.close()
	#db.close()
	return rv

#Iterates over sections, finds max bpm minus min bpm
#Adds a new column to merged_table of this value, for each song
def bpm_range(merged_dict, database_file):
	print "Calculating bpm ranges;"
	db = sqlite3.connect(database_file)
	db.text_factory = str
	cursor = db.cursor()
	cursor.execute("ALTER TABLE merged_table ADD bpm_range decimal(10,10)")
	rv = []
	for song in merged_dict.keys():
		beats = merged_dict[song]["beats"]
		beats = eval(beats)
		try:
			t = beats[0]["start"]
		except:
			#Some songs do not have detailed track information.
			#In this case, we set bpm_range (which should always be positive) to -1.
			print "bpm_range fails at: ",song
			cursor.execute("UPDATE merged_table SET bpm_range=? WHERE id=?", (-1, merged_dict[song]["id"]))
			continue
		min = 500.0
		max = 0.0
		range=0
		for beat in beats:
			bpm = 60.0/beat["duration"]
			if bpm > max:
				max = bpm
			if bpm < min:
				min = bpm
		range = round(max - min, 2)
		cursor.execute("UPDATE merged_table SET bpm_range=? WHERE id=?", (range, merged_dict[song]["id"]))
		db.commit()
		rv.append(range)
	#cursor.close()
	#db.close()
	return rv

#Counts number of "sections" in a song
def num_sections(merged_dict, database_file):
	print "Calculating num sections;"
	db = sqlite3.connect(database_file)
	db.text_factory = str
	cursor = db.cursor()
	rv = []
	cursor.execute("ALTER TABLE merged_table ADD num_sections INTEGER")
	for song in merged_dict.keys():
		sections = merged_dict[song]["sections"]
		sections = eval(sections)
		z = len(sections)
		rv.append(z)
		cursor.execute("UPDATE merged_table SET num_sections=? WHERE id=?", (z, merged_dict[song]["id"]))
		db.commit()
	#cursor.close()
	#db.close()
	return rv

#Iterates over sections, finds overall max key minus min key
#Adds a new column to merged_table of this value, for each song
def key_range(merged_dict, database_file):
	print "Calculating key ranges;"
	db = sqlite3.connect(database_file)
	db.text_factory = str
	cursor = db.cursor()
	cursor.execute("ALTER TABLE merged_table ADD key_range INTEGER")
	rv = []
	for song in merged_dict.keys():
		sections = merged_dict[song]["sections"]
		sections = eval(sections)
		try:
			k = sections[0]["key"]
		except:
			#Some songs do not have detailed track information.
			#In this case, we set key_range (which should always be positive) to -1.
			cursor.execute("UPDATE merged_table SET key_range=? WHERE id=?", (-1, merged_dict[song]["id"]))
			continue
		min = 50
		max = -1
		for section in sections:
			if section["key"] > max:
				max = section["key"]
			if section["key"] < min:
				min = section["key"]
		range = max - min
		range = round(range,2)
		cursor.execute("UPDATE merged_table SET key_range=? WHERE id=?", (range, merged_dict[song]["id"]))
		db.commit()
		rv.append(range)
	#cursor.close()
	#db.close()
	return rv

#Iterates over segments, finds largest sudden spike in bpm
#Adds a new column to merged_table of this value, for each song
def max_bpm_spike(merged_dict,database_file):
	print "Calculating max bpm spikes;"
	db = sqlite3.connect(database_file)
	db.text_factory = str
	cursor = db.cursor()
	cursor.execute("ALTER TABLE merged_table ADD max_bpm_spike decimal(10,10)")
	rv = []
	for song in merged_dict.keys():
		beats = merged_dict[song]["beats"]
		beats = eval(beats)
		try:
			k = beats[0]["duration"]
		except:
			#Some songs do not have detailed track information.
			#In this case, we set max_bpm_spike (which should always be positive) to -1.
			cursor.execute("UPDATE merged_table SET max_bpm_spike=? WHERE id=?", (-1, merged_dict[song]["id"]))
			continue
		max_range = 0
		prev = 60.0/beats[0]["duration"]
		for beat in beats:
			curr = 60.0/beat["duration"]
			range = abs(prev - curr)
			if range > max_range:
				max_range = range
			prev = curr
		max_range = round(max_range,3)
		cursor.execute("UPDATE merged_table SET max_bpm_spike=? WHERE id=?", (max_range, merged_dict[song]["id"]))
		db.commit()
		rv.append(max_range)
	#cursor.close()
	#db.close()
	return rv

#Iterates over sections, finds number of unique keys this song is in
#Adds a new column to merged_table of this value, for each song
def num_keys(merged_dict, database_file):
	print "Calculating num keys;"
	db = sqlite3.connect(database_file)
	db.text_factory = str
	cursor = db.cursor()
	cursor.execute("ALTER TABLE merged_table ADD num_keys INTEGER")
	rv = []
	for song in merged_dict.keys():
		sections = merged_dict[song]["sections"]
		sections = eval(sections)
		max_range = 0
		try:
			prev = sections[0]["key"]
		except:
			#Some songs do not have detailed track information.
			#In this case, we set num_keys (which should always be positive) to -1.
			cursor.execute("UPDATE merged_table SET num_keys=? WHERE id=?", (-1, merged_dict[song]["id"]))
			continue
		unique_keys = []
		for section in sections:
			if section["key"] not in unique_keys:
				unique_keys.append(section["key"])
		num_keys = len(unique_keys)
		cursor.execute("UPDATE merged_table SET num_keys=? WHERE id=?", (num_keys, merged_dict[song]["id"]))
		db.commit()
		rv.append(num_keys)
	#cursor.close()
	#db.close()
	return rv

def main():
	if len(sys.argv) > 1:
		database_file = sys.argv[1]
		big_dict = merge_retrieve(database_file)
		bpm_range(big_dict,database_file)
		key_range(big_dict,database_file)
		max_bpm_spike(big_dict,database_file)
		num_keys(big_dict,database_file)
		num_sections(big_dict,database_file)
	else:
		print "Usage: python process_info.py <database_file>"
		
if __name__ == "__main__":
	main()