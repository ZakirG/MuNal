#deletes/creates testing databases if necessary
#!/bin/bash
rm test_data/rap_test.db
touch test_data/rap_test.db
rm test_data/edm_test.db
touch test_data/edm_test.db
rm test_data/folk_test.db
touch test_data/folk_test.db

#Sample rap music
sqlite3 test_data/rap_test.db < sql/song_table.sql
sqlite3 test_data/rap_test.db < sql/track_table.sql

python song_query.py Rick\ Ross test_data/rap_test.db 20
python get_track_info.py test_data/rap_test.db Rick\ Ross

python song_query.py Pusha\ T test_data/rap_test.db 20
python get_track_info.py test_data/rap_test.db Pusha\ T

python song_query.py Kendrick\ Lamar test_data/rap_test.db 20
python get_track_info.py test_data/rap_test.db Kendrick\ Lamar

sqlite3 test_data/rap_test.db < sql/merge_tables.sql 
python process_info.py test_data/rap_test.db


#Sample edm music
sqlite3 test_data/edm_test.db < sql/song_table.sql
sqlite3 test_data/edm_test.db < sql/track_table.sql

python song_query.py Steve\ Aoki test_data/edm_test.db 20
python get_track_info.py test_data/edm_test.db Steve\ Aoki

python song_query.py Diplo test_data/edm_test.db 20
python get_track_info.py test_data/edm_test.db Diplo

python song_query.py Flux\ Pavilion test_data/edm_test.db 20
python get_track_info.py test_data/edm_test.db Flux\ Pavilion

sqlite3 test_data/edm_test.db < sql/merge_tables.sql
python process_info.py test_data/edm_test.db

#Sample folk music
sqlite3 test_data/folk_test.db < sql/song_table.sql
sqlite3 test_data/folk_test.db < sql/track_table.sql

python song_query.py Blitzen\ Trapper test_data/folk_test.db 20
python get_track_info.py test_data/folk_test.db Blitzen\ Trapper

python song_query.py Mumford\ and\ Sons test_data/folk_test.db 20
python get_track_info.py test_data/folk_test.db  Mumford\ and\ Sons

python song_query.py The\ Lumineers test_data/folk_test.db 20
python get_track_info.py test_data/folk_test.db The\ Lumineers

sqlite3 test_data/folk_test.db < sql/merge_tables.sql 
python process_info.py test_data/folk_test.db