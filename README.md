# mk3
Skripts to tinker with my music collection

Here I want to rewrite or refactor my already existing code fragments into reusable code. Goal is to build a software base to use for often dreamed future projects around my music collection.

I'm using Python, thinking about more docker and maybe kubernetes (if I see any useful reason for it besides playing with it!), AI in limited directions (I will not let AI make "music in the style of x with y as a singer and sounding like z in the 70s on his best album")

Purely hobby at this point. But I want to finally get better in things I started long ago, instead of starting something new. 

Jan. 21, 2024

As usual with projects like these and brainz like mine and work like in IT, this project had an unsuspected break. During this time I coded uncoordinated new features into the elasticsearch-branch I made. Today I merged a bunch of these features (without my local test scripts they seem not like much), and will go on a lil less chaotic and planned from here. But hey - my shøt works. 

Aug. 22, 2024

 ## What it does so far - Aug. 2024

Extracts tags from flac

Creates a redis worker queue (path and filename) out of a file tree with flacs and jpgs.

Takes a flac file and creates a mp3-file in a new position.

Adds cover.jpg from same source as flac-file folder to mp3-file.

Copies tags from flac to mp3.

Communicates with Musicbrainz (sends and receives IDs and data)

Writes and reads data into PostgreSQL

Dockerfile

A bit elasticsearch



