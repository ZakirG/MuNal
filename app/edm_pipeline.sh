#deletes/creates training databases if necessary
#!/bin/bash
rm genre_db/edm.db
touch genre_db/edm.db
sqlite3 genre_db/edm.db < sql/song_table.sql
sqlite3 genre_db/edm.db < sql/track_table.sql

#gets basic training data
python song_query.py Deadmau5 genre_db/edm.db
python get_track_info.py genre_db/edm.db Deadmau5

python song_query.py Skrillex genre_db/edm.db
python get_track_info.py genre_db/edm.db Skrillex

python song_query.py David\ Guetta genre_db/edm.db
python get_track_info.py genre_db/edm.db David\ Guetta

python song_query.py Alesso genre_db/edm.db
python get_track_info.py genre_db/edm.db Alesso

python song_query.py Swedish\ House\ Mafia genre_db/edm.db
python get_track_info.py genre_db/edm.db Swedish\ House\ Mafia

python song_query.py Avicii genre_db/edm.db
python get_track_info.py genre_db/edm.db Avicii

python song_query.py Zedd genre_db/edm.db
python get_track_info.py genre_db/edm.db Zedd

sqlite3 genre_db/edm.db < sql/merge_tables.sql 

#gets more detailed training data
python process_info.py genre_db/edm.db