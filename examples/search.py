import goifer

records = goifer.search('canton-zurich', query='Zurich')
print('')

for record in records:
    # print fields from schema
    print(record['reference'])
    print(record['title'])
    print(record['date'])
    print('')
