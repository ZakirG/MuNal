CREATE TABLE merged_table(
		song_name TEXT, 
		artist_name TEXT, 
		bpm decimal(10,10), 
		time_sig INTEGER, 
		key INTEGER, 
		id TEXT, 
		analysis_url TEXT,
		duration decimal(10,10), 
		speechiness decimal(10,10), 
		loudness decimal(10,10), 
		song_profile TEXT,
		bars TEXT, 
		segments TEXT,
		beats TEXT,
		sections TEXT, 
		tatums TEXT, 
		end_of_fade_in decimal(10,10), 
		start_of_fade_out decimal(10,10)
		);

INSERT INTO merged_table SELECT songs.song_name,songs.artist_name,songs.bpm,songs.time_sig, 
		songs.key,songs.id,songs.analysis_url,songs.duration,songs.speechiness, 
		songs.loudness,songs.song_profile,track_info.bars, track_info.segments,track_info.beats,
		track_info.sections, track_info.tatums, track_info.end_of_fade_in,track_info.start_of_fade_out
		FROM (track_info LEFT JOIN songs ON 
			songs.song_name=track_info.song_name AND songs.id=track_info.id);

DROP TABLE songs;
DROP TABLE track_info;