import goifer
from pprint import pprint

records = goifer.search('canton_zurich', index="sitzungsdetail", query='datum_start >= "2015-11-19 00:00:00" sortBy datum_end/sort.ascending uhrzeit/sort.ascending')
print('')

for record in records:
    pprint(record)
    print('')
