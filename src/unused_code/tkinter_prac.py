from Tkinter import *
import ttk
import read_songs_artist as rsa
import get_track_info as gti
import process_input as procinp
import pyen
import data_analysis as analys
import pickle

API_KEY = "GX5WDOWGQL5FJBBVF"
#setting the API key
en = pyen.Pyen("GX5WDOWGQL5FJBBVF")
CREDITS = '*********************\nMusic Analysis Project. \nMegan Barnes, Zakir Gowani, and Michael Lizza, Group 275. \n*********************\n'
HELP = """*********************\nThis program implements a decision tree using R to predict the genre of an input song. \n\
Enter a song name and an artist name in the fields provided. \n\
The Display Info button queries the Echonest music database for some information; other information is calculated from our own algorithms. \n\
Then select the Guess Genre button for our decision tree's prediction.\n\
The algorithm used here has approximately a 60% success rate when discriminated between inputs that fall in either Rap, EDM, or Folk.\n\
*********************\n"""


#These global variables refer to the clicked-or-not-clicked status of the two input fields
global clicked_field_1
clicked_field_1 = False
global clicked_field_2
clicked_field_2 = False

def callback_1(self):
	global clicked_field_1
	if clicked_field_1 == False:
		e1.delete(0,END)
		e1.config(fg = 'black')
		clicked_field_1 = True

def callback_2(self):
	global clicked_field_2
	if clicked_field_2 == False:
		e2.delete(0,END)
		e2.config(fg = 'black')
		clicked_field_2 = True

def show_entry_fields():
   print("Song Name: %s\nArtist: %s" % (e1.get(), e2.get()))

#Returns dictionary from echonest; function modified for use with GUI
def song_profile(named_input, artist, result_num=0):
	if artist == -1:
		id = rsa.song_search(named_input, result_num)
	else:
		id = rsa.song_search_artist(named_input, artist, result_num)
	if id == -1:
		return "No results for that query. \n"
	response = en.get('song/profile', api_key=API_KEY, id=id, bucket="audio_summary")
	return response["songs"][result_num]

#Prints summary of song and returns information necessary for decision tree
def query(name,artist):
	keys = ['C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb']
	if name == "" or artist == "":
		display_text("No results for that query. \n")
		return -1
	dict = song_profile(str(name),str(artist))
	if dict != "No results for that query. \n":
		dict2 = gti.get_json(dict['audio_summary']['analysis_url'])
		#print dict2.keys()
		tempo = dict['audio_summary']['tempo']
		time_sig = dict['audio_summary']['time_signature']
		speechiness = dict['audio_summary']['speechiness']
		artist_name = dict['artist_name']
		song = dict['title']
		key = keys[dict['audio_summary']['key']]
		duration = dict['audio_summary']['duration']
		loudness = dict['audio_summary']['loudness']
		bpm_range = procinp.bpm_range(dict2['beats'])
		max_bpm_spike = procinp.max_bpm_spike(dict2['beats'])
		num_sections = procinp.num_sections(dict2['sections'])
		try:
			num_keys = procinp.num_keys(dict2['sections'])
			num_keys_found = True
		except:
			num_keys_found = False
		a = "Song information:\n"
		b = "\t" + song + ", by " + artist_name + "\n"
		c = "\tTime signature: " + str(time_sig)+ "\n"
		d = "\tTempo: " + str(tempo)+ " beats per minute\n"
		e = "\tSpeechiness: " + str(speechiness)+ "\n"
		f = "\tLoudness: " + str(loudness)+ " decibels\n"
		g = "\tKey: " + str(key)+ "\n"
		h = "\tDuration: " + str(duration)+ " seconds\n"
		i = "\tTempo Range: "+str(bpm_range)+"\n"
		j = "\tMaximum Tempo Spike: "+str(max_bpm_spike)+"\n"
		k = "\tNumber of Sections: "+str(num_sections)+"\n"
		m = "\n"
		if num_keys_found:
			l = "\tNumber of Keys: "+str(num_keys)+"\n"
			display_text(a+b+c+d+e+f+g+h+i+j+k+l+m)
		else:
			display_text(a+b+c+d+e+f+g+h+i+j+k+m)
		return (dict,dict2)
	else:
		display_text(dict)
		return -1

#function for displaying text in scroll box
def display_text(dict):
	if dict != "No results for that query. \n" or dict != "Please enter a song name. \n":
		tex.insert(INSERT,dict,"success")
		tex.see(END)
		return
	else:
		tex.insert(INSERT,dict,"fail")
		tex.see(END)
		return

#function that guesses and displays the genre of the input song
def guess(name,artist):
	if name == "":
		a = "Please enter a song name. \n"
		display_text(a)
	dict1 = song_profile(str(name),str(artist))
	if dict1 == "No results for that query. \n":
		display_text(dict1)
		return
	dict2 = gti.get_json(dict1["audio_summary"]["analysis_url"])
	#url_dict = {dict1['title']: [dict1['audio_summary']['analysis_url'], dict1['id']]}
	#dict2 = gti.build_json_dict(url_dict)
	result = analys.classify_encapsulated(dict1,dict2,'genre_fit.pkl')
	a = "Genre guess for "+str(dict1['title'])+", by "+str(dict1['artist_name'])+": " + str(result[1]) + "\n"
	b = "\t" + str(round(result[0][0]*100,2)) + "%" + " probability this is EDM.\n"
	c = "\t" + str(round(result[0][1]*100,2)) + "%" + " probability this is Folk.\n"
	d = "\t" + str(round(result[0][2]*100,2)) + "%" + " probability this is Rap.\n\n"
	display_text(a+b+c+d)

master = Tk()
master.title("MuNal")
master.geometry("450x465+300+100")
master.configure(background='tomato2')
style=ttk.Style()
try:
	style.configure("TLabel",font='tahoma 9',foreground='black')
except: 
	style.configure("TLabel",font='helvetica 9',foreground='black')
photo = PhotoImage(file = 'images/yeezus1.gif')
photo2 = PhotoImage(file = 'images/help1.gif')
ttk.Label(master, text="Song Name",style='TLabel',background="tomato2").grid(row=0,column=2)
ttk.Label(master, text="Artist",style='TLabel',background="tomato2").grid(row=1,column=2)

v1 = StringVar()
v1.set("Blood on the Leaves")
e1 = Entry(master,textvariable=v1,font='helvetica 9', background="snow", foreground="gray")
e1.bind("<FocusIn>",callback_1)
e1.pack()

v2 = StringVar()
v2.set("Kanye West")
e2 = Entry(master,textvariable=v2,font='helvetica 9', foreground="gray")
e2.bind("<FocusIn>",callback_2)
e2.pack()

e1.grid(row=0, column=3)
e2.grid(row=1, column=3)


tex = Text(master=master, wrap=WORD)
tex.config(width=60,height=20,font='helvetica 9')
tex.tag_config("fail",foreground='red')
tex.tag_config("success",foreground='black')
tex.grid(row=5,column=0,columnspan=5,padx=6)


Button(master, image=photo, command= lambda: display_text(CREDITS)).grid(row=0, column=0, sticky=W,padx=4,pady=4,ipadx=5,ipady=5,rowspan=3,columnspan=3)
Button(master, text='Display Info', command=lambda: query(v1.get(),v2.get()),bg='white').grid(row=4, column=2, sticky=W, padx=1,pady=2)
Button(master, text='Guess Genre', command=lambda: guess(v1.get(),v2.get()),bg='white').grid(row=4, column=3, sticky=W, padx=1,pady=2)
Button(master, text='Quit', command=master.quit,bg='white').grid(row=6, column=4, sticky=W, padx=1,pady=2)
Button(master, image=photo2, command= lambda: display_text(HELP)).grid(row=6, column=0, sticky=W,padx=6,pady=3)



mainloop()
#master.destroy()
