from elasticsearch import Elasticsearch
import config
import mk3lib
import json

my_elas = Elasticsearch("http://localhost:9200")

print(my_elas.info())

update = True
myworkerqueue = mk3lib.WorkerQueue(config.queue,config.mk3_source,"\\.flac$")
counter = 0

while (True):
    myresult = myworkerqueue.get_next()
    if myresult != 'Done':
        counter = counter + 1
        print (counter)
        myflac = mk3lib.flactag(config.mk3_source, myresult[0], myresult[1])
        flac_string = json.loads(myflac.readfull())
        to_be_json = {}
        for i in flac_string:
            to_be_json[i[0]] = i[1]
        finally_json = json.dumps(to_be_json)
        my_elas.index(index="mk3-test", document=finally_json)
        #print(myflac.read_songid())

    else:
        break
