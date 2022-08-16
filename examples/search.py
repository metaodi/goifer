import goifer
from pprint import pprint

records = goifer.search(
    "canton_zurich",
    index="Behoerden",
    query="Gremiumtyp adj Fraktion sortBy name/sort.ascending",
)
print("")

for record in records:
    pprint(record)
    print("")
