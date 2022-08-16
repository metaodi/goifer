import goifer
from pprint import pprint

records = goifer.search(
    "canton_zurich",
    index="Wahlkreise",
    query="inaktiv = false sortBy name/sort.ascending",
)
print("")

all_records = [r for r in records]
pprint(all_records)
