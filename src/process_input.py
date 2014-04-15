#Calculates bpm range using the beats attribute
def bpm_range(merged_dict):
	beats = merged_dict
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
	return range

#Counts number of "sections" in a song
def num_sections(merged_dict):
	sections = merged_dict
	z = len(sections)
	return z


#Uses beats dictionary to calculate maximum bpm spike between adjacent beat segments
def max_bpm_spike(merged_dict):
	beats = merged_dict
	max_range = 0
	prev = 60.0/(beats[0]["duration"])
	for beat in beats:
		curr = 60.0/(beat["duration"])
		range = abs(prev - curr)
		if range > max_range:
			max_range = range
		prev = curr
	max_range = round(max_range,3)
	return max_range

#Iterates over sections, finds number of unique keys this song is in
def num_keys(merged_dict):
	sections = merged_dict
	max_range = 0
	unique_keys = []
	for section in sections:
		if section["key"] not in unique_keys:
			unique_keys.append(section["key"])
	num_keys = len(unique_keys)
	return num_keys