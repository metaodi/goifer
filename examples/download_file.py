import goifer
import os
from pprint import pprint
import requests

client = goifer.Client("canton_zurich", maximum_records=3)
records = client.search(
    index="KRVersand",
    query='datum_end < "2020-11-19 00:00:00" sortBy datum_start/sort.descending',
)

versand = records[0]
pprint(versand)

# download the file
for pos in versand["position"]:
    if not isinstance(pos["dokument"], list):
        pos["dokument"] = [pos["dokument"]]
    for doc in pos["dokument"]:
        edoc = doc["edocument"]
        download_path = os.path.join(".", edoc["filename"])
        r = requests.get(edoc["download_url"])
        print(f"Download file {edoc['filename']}...")
        with open(download_path, "wb") as f:
            for chunk in r.iter_content(1024):
                f.write(chunk)
