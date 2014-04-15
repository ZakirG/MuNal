rm megan.db
touch megan.db
sqlite3 megan.db < sql/song_table.sql
sqlite3 megan.db < sql/track_table.sql

python song_query.py Nicki\ Minaj megan.db
python get_track_info.py megan.db Nicki\ Minaj

sqlite3 megan.db < sql/merge_tables.sql

python process_info.py megan.db