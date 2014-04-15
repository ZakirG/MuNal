#deletes/creates training databases if necessary
#!/bin/bash
rm genre_db/rap.db
touch genre_db/rap.db
sqlite3 genre_db/rap.db < sql/song_table.sql
sqlite3 genre_db/rap.db < sql/track_table.sql

#gets basic training info
python song_query.py Nicki\ Minaj genre_db/rap.db
python get_track_info.py genre_db/rap.db Nicki\ Minaj

python song_query.py Nas genre_db/rap.db
python get_track_info.py genre_db/rap.db Nas

python song_query.py Kanye\ West genre_db/rap.db
python get_track_info.py genre_db/rap.db Kanye\ West

python song_query.py Common genre_db/rap.db
python get_track_info.py genre_db/rap.db Common

python song_query.py Jay-Z genre_db/rap.db
python get_track_info.py genre_db/rap.db Jay-Z

python song_query.py Lil\ Wayne genre_db/rap.db
python get_track_info.py genre_db/rap.db Lil\ Wayne

python song_query.py Drake genre_db/rap.db
python get_track_info.py genre_db/rap.db Drake

sqlite3 genre_db/rap.db < sql/merge_tables.sql

#gets more detailed training info
python process_info.py genre_db/rap.db