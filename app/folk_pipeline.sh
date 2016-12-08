#deletes/creates training databases if necessary
#!/bin/bash
rm genre_db/folk.db
touch genre_db/folk.db
sqlite3 genre_db/folk.db < sql/song_table.sql
sqlite3 genre_db/folk.db < sql/track_table.sql

#gets basic training data
python song_query.py Jack\ Johnson genre_db/folk.db
python get_track_info.py genre_db/folk.db Jack\ Johnson

python song_query.py Tegan\ and\ Sara genre_db/folk.db
python get_track_info.py genre_db/folk.db Tegan\ and\ Sara

python song_query.py Fleet\ Foxes genre_db/folk.db
python get_track_info.py genre_db/folk.db Fleet\ Foxes

python song_query.py Simon\ and\ Garfunkel genre_db/folk.db
python get_track_info.py genre_db/folk.db Simon\ and\ Garfunkel

python song_query.py Bob\ Dylan genre_db/folk.db
python get_track_info.py genre_db/folk.db Bob\ Dylan

python song_query.py Bon\ Iver genre_db/folk.db
python get_track_info.py genre_db/folk.db Bon\ Iver

python song_query.py Beirut genre_db/folk.db
python get_track_info.py genre_db/folk.db Beirut

python song_query.py Elliot\ Smith genre_db/folk.db
python get_track_info.py genre_db/folk.db Elliot\ Smith

python song_query.py John\ Mayer genre_db/folk.db
python get_track_info.py genre_db/folk.db John\ Mayer

sqlite3 genre_db/folk.db < sql/merge_tables.sql

#gets more detailed training data
python process_info.py genre_db/folk.db