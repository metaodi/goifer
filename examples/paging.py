import goifer

client = goifer.Client("canton_zurich", maximum_records=3)
records = client.search(
    index="SitzungenDetail",
    query='datum_start >= "2019-11-19 00:00:00" and datum_end < "2020-01-07 00:00:00" sortBy datum_end/sort.ascending uhrzeit/sort.ascending',
)
print(f"Start: {records.maximum_records}")
print(f"Next: {records.next_start_record}")
print(f"Maximum: {records.maximum_records}")
print(f"Count: {records.count}")

print("")

# the paging of the API is transparent to the user of goifer
# if more data is needed, it is lazy loaded when needed
for record in records:
    print(f"Next start record: {records.next_start_record}")
    print(
        f"Datum: {record['datum_start'].strftime('%d.%m.%Y')}, Titel: {record['titel']}"
    )
    print("")
