# ##############################################################
# This script processes the SQL databases. 
# The rpy2 package is accessed to build a decision tree using housed R script.
# Contains many functions for translation between R and SQL, and production of test statistics
# ##############################################################
import pyen
import matplotlib.pyplot as plt
import sys, string, re
import sqlite3
import read_songs
import rpy2
import rpy2.robjects as robjects
from rpy2.robjects.packages import importr
from collections import defaultdict
import pickle
import process_input as proc


WATCH_FOR_MISSING_VALUES = [
							"loudness_range", "bpm_range", "key_range", 
							"max_loudness_spike","max_bpm_spike","num_keys"
							]

def vector_db(database_file):
	"""Retrieves information from one songs table in database file; returns a dictionary"""
	db = sqlite3.connect(database_file)
	cursor = db.cursor()
	speechiness,bpm,key,duration,loudness= [],[],[],[],[]
	end_of_fade_in,start_of_fade_out,loudness_range,bpm_range,key_range = [],[],[],[],[]
	max_loudness_spike,max_bpm_spike,num_keys = [],[],[]
	time_sig,num_sections = [], []
	fail_count = 0
	rv = {}
	song_data = cursor.execute("SELECT DISTINCT speechiness,bpm,key,duration,loudness, \
					end_of_fade_in,start_of_fade_out,bpm_range, \
					max_bpm_spike,num_keys,time_sig,num_sections FROM merged_table;")
	for row in song_data:
		speechiness.append(row[0])
		bpm.append(row[1])
		key.append(row[2])
		duration.append(row[3])
		loudness.append(row[4])
		end_of_fade_in.append(row[5])
		start_of_fade_out.append(row[6])
		if (not isinstance(row[7], float)) or (row[7] == -1):
			bpm_range.append("NA")
		else:
			bpm_range.append(row[7])
		if (not isinstance(row[8], float)) or (row[8]) == -1:
			fail_count += 1
			max_bpm_spike.append("NA")
		else:
			max_bpm_spike.append(row[8])
		if (not isinstance(row[9], int)) or (row[9] == -1):
			num_keys.append("NA")
		else:
			num_keys.append(row[9])
		time_sig.append(row[10])
		num_sections.append(row[11])
	rv["speechiness"] = speechiness
	rv["bpm"] = bpm
	rv["key"] = key
	rv["duration"] = duration
	rv["loudness"] = loudness
	rv["end_of_fade_in"] = end_of_fade_in
	rv["start_of_fade_out"] = start_of_fade_out
	rv["bpm_range"] = bpm_range
	rv["max_bpm_spike"] = max_bpm_spike
	rv["num_keys"] = num_keys
	rv["time_sig"] = time_sig
	rv["num_sections"] = num_sections
	#cursor.close()
	#db.close()
	return rv

def build_data_frame(sql_dict, names):
	"""Takes dictionary from vector_db, returns an R data frame object
	This code fills a placeholder dictionary of item type list, flattens list
	We use defaultdict to improve performance, and transpose the input.
	"""
	d = defaultdict(list)
	i = 0
	for category_data in sql_dict:
		for attribute_list in category_data:
			for attribute in category_data[attribute_list]:
				d[attribute_list].append(attribute)
		d["category"].extend([names[i]]* len(category_data[attribute_list]) )
		d["fct"].extend([i] * len(category_data[attribute_list]) )
		i += 1
	#Translation into R objects
	for attribute_list in d:
		if attribute_list == "category":
			d[attribute_list] = robjects.StrVector(d[attribute_list])
		elif attribute_list in WATCH_FOR_MISSING_VALUES:
			tmp = robjects.FloatVector(range(len(d[attribute_list])))
			for i in range(len(d[attribute_list])):
				if d[attribute_list][i] == "NA":
					tmp.rx[i] = robjects.NA_Real
				else:
					tmp.rx[i] =  d[attribute_list][i]
			d[attribute_list] = tmp
		else:
			if attribute_list == "num_sections":
				tmp = []
				for element in d[attribute_list]:
					if element == None:
						tmp.append(1)
					else:
						tmp.append(float(element))
				d[attribute_list] = robjects.FloatVector(tmp)
				continue
			elif attribute_list == "speechiness":
				tmp = []
				for element in d[attribute_list]:
					if element == None:
						tmp.append(1)
					else:
						tmp.append(float(element))
				d[attribute_list] = robjects.FloatVector(tmp)
				continue
				 
			else:
				d[attribute_list] = robjects.FloatVector(d[attribute_list])
	data_frame = robjects.DataFrame(d)
	return data_frame

def remove_outliers(data_frame, attribute, n):
	"""Remove samples for which attribute is n SD away from mean"""
	r = robjects.r
	robjects.globalenv["dat"] = data_frame
	new_frame = r("dat[!(abs(dat$"+attribute+" - mean(dat$"+attribute+ \
						"))/sd(dat$"+attribute+")) >" +str(n)+",]")
	return new_frame

def decision_tree(data_frame, filename=0):
	"""Takes return value of build_data_frame, a data frame containing information for all categories
	Moves to the left branch when the stated condition is true
	"""
	print "Building decision tree..."
	r = robjects.r
	rpart = importr("rpart")
	fit = rpart.rpart("category~bpm+speechiness+time_sig+key+duration+loudness+\
			end_of_fade_in+start_of_fade_out+bpm_range+\
			max_bpm_spike+num_keys", data=data_frame, method="class", 
			na_action='na.rpart', control='rpart.control(cp = .0001)')
	rpart.printcp(fit)
	r.plot(fit, uniform=True, main="Classification Tree for Genre")
	r.text(fit, use_n=True, all=True, cex=.8)
	if filename != 0:
		rpart.post(fit, file=filename, title="Classification Tree for Genre")
	raw_input("> Press enter to continue.")
	return fit

def prob_category(new_music, fit):
	"""Takes the return value of decision_tree (a fit) and a set of new, non-classified data in a data frame
	Returns a probability matrix, containing probabilities that given song is in a genre
	"""
	r = robjects.r
	#Be careful not to include the word 'data' in the function call below, although data is a keyword
	predictions = r.predict(fit,new_music,type="prob")
	return predictions

def classify(new_music,fit):
	"""Classifies new database songs, returns a matrix of probabilities that a song falls in a category"""
	r = robjects.r
	p = prob_category(new_music,fit)
	robjects.globalenv["pred"] = p
	r("""
	tmp3 = vector()
	for(i in 1:length(pred[,1])){
		xx <- unlist(pred[i,])
		tmp3 <- append(tmp3,which(xx==max(xx)))
	}
	classes <- names(tmp3)
	""")
	return list(robjects.globalenv["classes"])

def classify_encapsulated(audio_summary, track_info, pickle_file):
	"""Performs a similar operation to classify() and all the above functions in one step
	But retrieves fit from pickle, for the GUI
	"""
	f = open(pickle_file, 'r')
	fit = pickle.load(f)
	f.close()
	rv = {}
	#print track_info.keys()
	#print track_info[audio_summary]['title'].keys()
	rv["speechiness"] = [audio_summary['audio_summary']['speechiness']]
	rv["time_sig"] = [audio_summary['audio_summary']['time_signature']]
	rv["bpm"] = [audio_summary['audio_summary']['tempo']]
	rv["key"] = [audio_summary['audio_summary']['key']]
	rv["duration"] = [audio_summary['audio_summary']['duration']]
	rv["loudness"] = [audio_summary['audio_summary']['loudness']]
	rv["end_of_fade_in"] = [track_info['track']['end_of_fade_in']]
	rv["start_of_fade_out"] = [track_info['track']['start_of_fade_out']]
	rv["bpm_range"] = [proc.bpm_range(track_info['beats'])]
	rv["max_bpm_spike"] = [proc.max_bpm_spike(track_info['beats'])]
	try:
		rv["num_keys"] = [proc.num_keys(track_info['sections'])]
	except:
		rv["num_keys"] = [1]
	rv["sections"] = [proc.num_sections(track_info['sections'])]
	new_df = build_data_frame([rv],["Unknown"])
	p = prob_category(new_df,fit)
	robjects.globalenv["pred"] = p
	edm_prob = robjects.default_ri2py(p.rx(1))[0]
	folk_prob = robjects.default_ri2py(p.rx(2))[0]
	rap_prob = robjects.default_ri2py(p.rx(3))[0]
	cls = classify(new_df,fit)
	return [(edm_prob,folk_prob,rap_prob),cls[0]]

def successes(predictions,truth):
	"""Returns number of correct predictions"""
	total = len(predictions)
	correct = 0.0
	for p in predictions:
		if p == truth:
			correct += 1
		else:
			print truth,"\t",p
	return correct

def success_rate(predictions_list,truth_list):
	"""Returns success rate"""
	total,correct = 0,0
	for i in range(len(truth_list)):
		correct += successes(predictions_list[i],truth_list[i])
		total += len(predictions_list[i])
	return correct/total

def main():
	if len(sys.argv) < 2:
		categories = ["Rap", "EDM", "Folk"]
		genre_db = ["genre_db/rap.db","genre_db/edm.db","genre_db/folk.db"]
		data = []
		for db in genre_db:
			data.append(vector_db(db))
		data_frame = build_data_frame(data, categories)
		fit = decision_tree(data_frame) 
		f = open("genre_fit.pkl",'w')
		pickle.dump(fit,f)
		f.close()
	else:
		f = open("genre_fit.pkl",'r')
		r = robjects.r
		rpart = importr("rpart")
		fit = pickle.load(f)
		f.close()
		#rpart.printcp(fit)
		r.plot(fit, uniform=True, main="Classification Tree for Genre")
		r.text(fit, use_n=True, all=True, cex=.8)
		raw_input("> Press enter to continue.")
	#Testing success rate:
	genre1 = vector_db("test_data/rap_test.db")
	genre2 = vector_db("test_data/edm_test.db")
	genre3 = vector_db("test_data/folk_test.db")
	genre1_df = build_data_frame([genre1], ["Unknown"])
	genre2_df = build_data_frame([genre2], ["Unknown"])
	genre3_df = build_data_frame([genre3], ["Unknown"])
	p1 = classify(genre1_df, fit)
	p2 = classify(genre2_df, fit)
	p3 = classify(genre2_df, fit)
	#print "Success rate rap: ",success_rate([p1],["Rap"])
	#print "Success rate edm: ",success_rate([p2],["EDM"])
	#print "Success rate folk: ",success_rate([p3],["Folk"])
	print success_rate([p1,p2,p3],["Rap","EDM","Folk"])
	
if __name__ == "__main__":
	main()