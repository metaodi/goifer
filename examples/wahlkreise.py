import goifer
from pprint import pprint

records = goifer.search('canton_zurich', index="wahlkreise", query='inaktiv = false sortBy name/sort.ascending')
print('')

for record in records:
    pprint(record)
    print('')
