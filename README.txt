ituneslib

==============================

Skills:

SQL
Python
XML
xml.etree.ElementTree

==============================

Description:

This python script analyzes an xml Itunes library and extracts data of all the
songs present (song name, artist name, album name and play count) and stores that info
in a relational SQL database. Then it searches for the most played song or songs and the 
most played artists, and finally stores that info in a txt file, together with the list 
of artists found, the list of albums found, and the list of genres found, ordered
alphabetically.

Note: the code can be easily modified to enable the user to choose how many most played 
artists to show. The current value is 10 artists, but by commenting/uncommenting a couple
of lines, this can be modified.

==============================

Running the code:

-From windows command prompt, execute the .py file by writing "python filename.py"

==============================

Requirements:

-Python 3.7.1 or superior installed

==============================

Output:

-txt file (.txt) with the most played song or songs, the whole list of songs in the library
ordered by play count, the top 10 most played artists, and the lists of artists, albums 
and genres and their count.
-sqlite relational database file (.sqlite) with a Track table, an artist table, an album
table and a genre table

==============================

Files uploaded:

-python script: ituneslib.py
-Output files (as example): ituneslibrary.txt and ituneslibrary.sqlite
-Output: screenshots of sqlite database and txt file
-XML file: screenshot of the file