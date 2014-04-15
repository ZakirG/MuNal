#!/bin/bash
rm artist_db/kanye.db
touch artist_db/kanye.db
rm artist_db/skrillex.db
touch artist_db/skrillex.db
rm artist_db/jack_johnson.db
touch artist_db/jack_johnson.db

#Kanye West
sqlite3 artist_db/kanye.db < sql/song_table.sql
sqlite3 artist_db/kanye.db < sql/track_table.sql
python song_query.py Kanye\ West artist_db/kanye.db
python get_track_info.py artist_db/kanye.db Kanye\ West
sqlite3 artist_db/kanye.db < sql/merge_tables.sql 

#Skrillex
sqlite3 artist_db/skrillex.db < sql/song_table.sql
sqlite3 artist_db/skrillex.db < sql/track_table.sql
python song_query.py Skrillex artist_db/skrillex.db
python get_track_info.py artist_db/skrillex.db Skrillex
sqlite3 artist_db/skrillex.db < sql/merge_tables.sql 

#Jack Johnson
sqlite3 artist_db/jack_johnson.db < sql/song_table.sql
sqlite3 artist_db/jack_johnson.db < sql/track_table.sql
python song_query.py Jack\ Johnson artist_db/jack_johnson.db
python get_track_info.py artist_db/jack_johnson.db Jack\ Johnson
sqlite3 artist_db/jack_johnson.db < sql/merge_tables.sql