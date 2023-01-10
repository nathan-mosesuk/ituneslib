import xml.etree.ElementTree as xmltree, sqlite3

filexml=input('Enter Itunes library .xml file: ')

filename=filexml.replace('.xml','.txt')
filew=open(filename,'w')

filename=filexml.replace('.xml','.sqlite')
con=sqlite3.connect(filename)
cur=con.cursor()

counter=int()
repcount=int()
nonecount=int()
topartists=list()

#CREATE TABLES, AND DELETE IF ALREADY CREATED

cur.executescript('''
drop table if exists Artist;
drop table if exists Album;
drop table if exists Genre;
drop table if exists Track;
create table Artist(id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,artist TEXT UNIQUE);
create table Album(id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,album TEXT UNIQUE);
create table Genre(id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,genre TEXT UNIQUE);
create table Track(id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,track TEXT,playcount INTEGER,artist_id INTEGER,album_id INTEGER,genre_id INTEGER);
''')

#NOTE: Which table will each table point to?

#Criteria: an album may have songs of different genres and an album may have songs of different artists (a compilation).
#Artist table points to nobody
#Album table points to nobody
#Genre table points to nobody
#Track table points to Album and Genre and Artist, saving repetition of artist, album and genre names.
#The foreign key artist_id is in Track because different artists can call their song with the same name
#If there are songs without album name, they remain linked to the Artist as the foreign key is in Track.

#PARSE XML FILE AND PRINT NUM. OF TRACKS FOUND

print('\nAnalyzing xml file...\n')

xmldata=xmltree.parse(filexml) #reads and analizes filexml and stores data in an xml tree
tracks=xmldata.findall('dict/dict/dict') #searches for tags dict/dict/dict in the xml file. In this case don't ommit root tag dict.

#XML file structure
#<dict>
#   <dict>
#      <key>
#      <dict> # 1st song tag and subtags
#         <key>TAGNAME</key><variabletype>TAGVALUE</variabletype>
#      <key>
#      <dict> # 2nd song tag and subtags, etc.
#         <key>TAGNAME</key><variabletype>TAGVALUE</variabletype>

wordprint='Tracks found: '+str(len(tracks))+'\n'
print(wordprint)
filew.write(wordprint)

#DEFINE FUNCTION LOOKFORTAG, SEARCHES FOR A TAG INSIDE EACH TRACK

def lookfortag(textcontent):
   tagfound=False
   for tag in track: # this loops in each individual line of tags in all tags for 1 song
      if tagfound is True: return tag.text #returns the text of the next tag. This line is here because we want the following tag text.
      if tag.tag=='key' and tag.text==textcontent: tagfound=True #if the tag name is 'key' and the text matches textcontent...
      # if we find the tag we we're looking for, the info we want will be in the next tag text.
   return None

#LOOK FOR TAGS AND RETRIEVE TAG TEXT, THEN INSERT IN TABLES

repcount=0
nonecount=0
tagfound=False
line=''
for track in tracks: # tracks is all songs found (all groups of tags), and track is all tags for 1 song. The number of tracks is the number of songs present.
   artistx=lookfortag('Artist') #looks for tag key with text Artist.
   albumx=lookfortag('Album') #looks for tag key with text Album.
   genrex=lookfortag('Genre')
   trackx=lookfortag('Name')
   playcountx=lookfortag('Play Count')
   #the order in which the lookups are done doesn't matter because the search is done from scratch

   if trackx is None: #only if the track has no name it's ommits the track
      nonecount=nonecount+1
      continue

   #IF THERE'S NO ARTIST, ALBUM OR GENRE NAME, PUT NO...NAME

   if artistx is None: artistx='No Artist Name'
   if albumx is None: albumx='No Album Name'
   if genrex is None: genrex='No Genre Name'
   if playcountx is None: playcountx=0

   #SQL: INSERT DATA INTO TABLES

   cur.execute('insert or ignore into Artist (artist) values (?)',(artistx,))
   cur.execute('select id from Artist where artist=?',(artistx,)) # select the id from Artist, automatically created
   artistid=cur.fetchone()[0] # retrieve the id, first one found (and only one in this case)

   cur.execute('insert or ignore into Album (album) values (?)',(albumx,))
   cur.execute('select id from Album where album=?',(albumx,)) # select the id from Album, automatically created
   albumid=cur.fetchone()[0] # retrieve the id, first one found (and only one in this case)
   
   cur.execute('insert or ignore into Genre (genre) values (?)',(genrex,))
   cur.execute('select id from Genre where genre=?',(genrex,)) # select the id from Genre, automatically created
   genreid=cur.fetchone()[0] # retrieve the id, first one found (and only one in this case)

   cur.execute('insert or ignore into Track (track,playcount,artist_id,album_id,genre_id) values (?,?,?,?,?)',(trackx,playcountx,artistid,albumid,genreid))
   # playcountx is converted to integer here, because playcount in table Track is type integer (except when playcountx is 0)

#PRINT OMMITED TRACKS BECAUSE OF MISSING INFO

wordprint='Tracks with missing info: '+str(nonecount)+'\n'
print(wordprint)
wordprint='\n'+wordprint
filew.write(wordprint)

#PRINT THE MOST PLAYED SONG(S) (1 or more)

cur.execute('''select Track.playcount,Track.track,Artist.artist,Album.Album from Artist join Album join Track on
           Track.album_id=Album.id and Track.artist_id=Artist.id ORDER BY Track.playcount DESC''')
mostplayed=cur.fetchall() #fetchall creates a list of tuples, with all the rows selected

wordprint='Most played song or songs:\n'
print(wordprint)
wordprint='\n'+wordprint+'\n'
filew.write(wordprint)

# This loop will look for the most played song (1st in the list) and any other subsequent song with the same playcount.

previouscount=0
for field in mostplayed: # field is a tuple of 4 elements.
   if field[0]==0:
      if previouscount==0:
         wordprint='Most played song: all songs have 0 plays.'
         print(wordprint)
         wordprint='\n'+wordprint+'\n'
         filew.write(wordprint)
      break #if the song doesn't have any plays, because tag 'Play Count' is absent.
   if field[0]<previouscount: break #if the current play count is smaller than the one before, break.

   wordprint=field[1]+' ** by: '+field[2]+' ** Album: '+field[3]+' ** Plays: '+str(field[0]) # field[0] is an int
   print(wordprint)
   filew.write(wordprint)

   previouscount=field[0]

#WRITE ALL SONG(S) TO FILE .TXT
#AND IN THE SAME LOOP, SEARCH FOR THE MOST PLAYED ARTISTS

#artnum=input('Enter num. of top artists wanted: ') # ============ UNCOMMENT THIS LINE AND THE ONE BELOW TO INQUIRE THE USER FOR THE NUMBER
#artnumi=int(artnum)
artnumi=10 # ============ IF SO, COMMENT THIS LINE. MODIFY THIS NUMBER TO SHOW A DIFFERENT NUMBER OF TOP ARTISTS

artcount=0
previousart='' # it will compare the current artist name with the previos one

wordprint='\nSongs list\n\nPlay_count Song_name Artist Album\n'
wordprint='\n'+wordprint+'\n'
filew.write(wordprint)

for field in mostplayed:
   wordprint=str(field[0])+' ** '+field[1]+' ** by: '+field[2]+' ** Album: '+field[3]+'\n' #field[0] is an integer and has to be converted to str
   try:
      filew.write(wordprint)
   except: #if the track title has invalid characters, write WRONG TRACK TITLE
      wordprint=str(field[0])+' ** '+'WRONG TRACK TITLE'+' ** by: '+field[2]+' ** Album: '+field[3]+'\n' #field[0] is an integer and has to be converted to str
      filew.write(wordprint)

#SEARCH FOR THE MOST PLAYED ARTISTS. Fill up list topartists if the artist Field[2] is not in the list already.

   if previousart==field[2]: continue #if the current artist is the same as the previous one, skip it. This saves doing the code below.
   artfound=False #artfound always has to start in False, otherwise it will interpret that the artist is found in the list topartists already
   if artcount<artnumi: #artcount is an index for the list, and artnumi is the number of most played artists wanted
      for topartist in topartists: #checks if the current artist is already in the list. If so, True.
         if topartist==field[2]: 
            artfound=True # artfound is True, only if the artist is already in the list
            previousart=field[2] #previousart is the previous artist, has to be updated. Now field[2] is the new previousart
      if artfound is False: #if the artist is not in the list already, add it to it
         topartists.append(field[2])
         artcount=artcount+1
         artfound=False #resets artfound to False, like in the beginning, to start again
         previousart=field[2]

#PRINT THE MOST PLAYED ARTISTS

artcount=1
print('\nThe',artnumi,'most played artists are: \n')
line='\nThe '+str(artnumi)+' most played artists are:\n\n'
filew.write(line)
for topartist in topartists:
   print(artcount,topartist)
   line=str(artcount)+' '+topartist+'\n'
   filew.write(line)
   artcount=artcount+1

i=artcount
while i<=artnumi: # if artnumi is 10 we want the list up to 10 not 9
   print(i,'N/A')
   wordprint=str(i)+' N/A\n'
   filew.write(wordprint)
   i=i+1
filew.write('\n')

#PRINT ARTISTS IN LIBRARY

#print('\n') # ============ UNCOMMENT THESE 3 LINES TO INQUIRE THE USER ABOUT STORING THE ARTISTS AND ALBUMS LIST.
#printall=input('Show and save artists and albums list? Yes/No:')
#print('\n')
printall='Yes' # ============ IF SO, COMMENT THIS LINE

wordprint='Artists\n\n'
filew.write(wordprint)

artcount=1
cur.execute('select Artist.artist from Artist order by Artist.artist ASC')
artistlist=cur.fetchall()
for artistl in artistlist:
   if printall=='Yes': 
      line=str(artcount)+' '+artistl[0]+'\n' # [0] is because artistl is a tuple (of 2 items) and I only want to print the first
      try: filew.write(line)
      except: 
         line=str(artcount)+' '+'INVALID ARTIST NAME\n'
         filew.write(line)
   artcount=artcount+1
artcount=artcount-1
print('\nArtists in library:',artcount)
line='\nArtists in library: '+str(artcount)+'\n\n'
filew.write(line)

#PRINT ALBUMS IN LIBRARY

wordprint='\nAlbums\n\n'
filew.write(wordprint)

albcount=1
cur.execute('select Album.album from Album order by Album.album ASC')
albumlist=cur.fetchall()
for albuml in albumlist:
   if printall=='Yes': 
      line=str(albcount)+' '+albuml[0]+'\n' # [0] is because artistl is a tuple (of 2 items) and I only want to print the first
      try: filew.write(line)
      except: 
         line=str(albcount)+' '+'INVALID ALBUM NAME\n'
         filew.write(line)
   albcount=albcount+1
albcount=albcount-1
print('\nAlbums in library:',albcount)
line='\nAlbums in library: '+str(albcount)+'\n\n'
filew.write(line)

#PRINT GENRES IN LIBRARY

wordprint='\nGenres\n\n'
filew.write(wordprint)

gencount=1
cur.execute('select Genre.genre from Genre order by Genre.genre ASC')
genrelist=cur.fetchall()
for genrel in genrelist:
   if printall=='Yes': 
      line=str(gencount)+' '+genrel[0]+'\n' # [0] is because genrel is a tuple (of 2 items) and I only want to print the first
      try: filew.write(line)
      except: 
         line=str(gencount)+' '+'INVALID GENRE NAME\n'
         filew.write(line)
   gencount=gencount+1
gencount=gencount-1
print('\nGenres in library:',gencount)
line='\nGenres in library: '+str(gencount)+'\n'
filew.write(line)

con.commit()
