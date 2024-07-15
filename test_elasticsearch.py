from elasticsearch import Elasticsearch
import json

#my_elas = Elasticsearch("http://localhost", 9200)
my_elas = Elasticsearch("http://localhost:9200")

print(my_elas.info())

json_string = [["MUSICBRAINZ_RELEASEGROUPID", "9eb48d7e-2425-32d9-8d0b-54903d4a66be"], ["ORIGINALDATE", "1972-06"], ["ORIGINALYEAR", "1972"], ["RELEASETYPE", "album"], ["MUSICBRAINZ_ALBUMID", "e1271ab8-d308-433d-bd74-e7e478af22f3"], ["MUSICBRAINZ_ALBUMARTISTID", "51625f3d-adfa-4096-a7b9-113f5225cc58"], ["ALBUMARTIST", "Aphrodite's Child"], ["ALBUMARTISTSORT", "Aphrodite's Child"], ["ALBUM", "666"], ["ASIN", "B000007TVK"], ["RELEASESTATUS", "official"], ["BARCODE", "042283843028"], ["DATE", "1989-08-22"], ["SCRIPT", "Latn"], ["LABEL", "Vertigo"], ["CATALOGNUMBER", "838 430-2"], ["RELEASECOUNTRY", "DE"], ["TOTALDISCS", "2"], ["MEDIA", "CD"], ["DISCNUMBER", "2"], ["TOTALTRACKS", "8"], ["MUSICBRAINZ_TRACKID", "48359b66-701d-4dac-929a-a3505132e80d"], ["MUSICBRAINZ_ARTISTID", "51625f3d-adfa-4096-a7b9-113f5225cc58"], ["ARTIST", "Aphrodite's Child"], ["ARTISTSORT", "Aphrodite's Child"], ["ARTISTS", "Aphrodite's Child"], ["TITLE", "Seven Trumpets"], ["ISRC", "NLF050390215"], ["MUSICBRAINZ_RELEASETRACKID", "61c082bd-20f7-4ff3-9beb-c60a405d2e9e"], ["TRACKNUMBER", "1"], ["ACOUSTID_ID", "283b1530-368e-4023-8e10-095a7ec3c795"], ["TRACKTOTAL", "8"], ["DISCTOTAL", "2"]]
print (json_string)
print("\nHere")
json_dumps = json.dumps(json_string)
json_object = json.loads(json_dumps)
print (type(json_string))
print (type(json_dumps))
print (type(json_object))
print("There")
