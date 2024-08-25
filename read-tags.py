#!/usr/bin/python3

import config
import mk3lib

myworkerqueue = mk3lib.WorkerQueue(config.queue, config.mk3_source, "\\.flac$")
my_artistlist = set()

x = 0

while (True):
    myresult = myworkerqueue.get_next()
    if myresult != 'Done':
        myflac = mk3lib.flactag(config.mk3_source, myresult[0], myresult[1])
        # print(myflac.readfull())
        albumartistid = myflac.read_albumartistids()
        albumartist = myflac.read_albumartist()
        print(albumartistid, albumartist)
        for artistid in albumartistid:
            my_artistlist.add((artistid, albumartist))
    else:
        break

for i in my_artistlist:
    print(i[0],"+++", i[1])