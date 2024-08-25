from elasticsearch import Elasticsearch
import config


class scatterbrain:
    def __init__(self):
        self.elasearch = Elasticsearch("http://localhost:9200")
        self.index_name = config.index_name
        # self.elasearch.indices.create(index=self.index_name)
        # todo: create if not present

    def drop_flac(self,song_id,tag_json_string):
        print(song_id)
        print(tag_json_string)
        self.elasearch.bulk(
            index=self.index_name,
            body=tag_json_string,
            doc_type=None
        )
