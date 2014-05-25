# #########################################################
# This script creates new statistics for the decision tree fit. 
# Handles sql databases of large size, of genre categories. 
# Statistics calculated include bpm_range, number of sections, number of keys the song is in, and maximum bpm spike.
# #########################################################

def bpm_range(merged_dict):
	"""Calculates bpm range using the beats attribute"""
	beats = merged_dict
	min = 500.0
	max = 0.0
	range=0
	for beat in beats:
		bpm = 60.0 / beat["duration"]
		if bpm > max:
			max = bpm
		if bpm < min:
			min = bpm
	range = round(max - min, 2)
	return range

def num_sections(merged_dict):
	"""Counts number of "sections" in a song"""
	sections = merged_dict
	z = len(sections)
	return z

def max_bpm_spike(merged_dict):
	"""Uses beats dictionary to calculate maximum bpm spike between adjacent beat segments"""
	beats = merged_dict
	max_range = 0
	prev = 60.0 / (beats[0]["duration"])
	for beat in beats:
		curr = 60.0 / (beat["duration"])
		range = abs(prev - curr)
		if range > max_range:
			max_range = range
		prev = curr
	max_range = round(max_range,3)
	return max_range

def num_keys(merged_dict):
	"""Iterates over sections, finds number of unique keys this song is in"""
	sections = merged_dict
	max_range = 0
	unique_keys = []
	for section in sections:
		if section["key"] not in unique_keys:
			unique_keys.append(section["key"])
	num_keys = len(unique_keys)
	return num_keys