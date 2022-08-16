import goifer
import requests
from pprint import pprint

# sometime is't necessary to tweak the requests Session (e.g. to provide authentication, set a custom header or disable SSL verification). For this purpose a customized session can be passed to the Client

session = requests.Session()
session.verify = False  # disable SSL verification

client = goifer.Client("canton_zurich", maximum_records=1000, session=session)
records = client.search(index="Ablaufschritte", query="seq>2075771")

print(records)
pprint(records[0])
