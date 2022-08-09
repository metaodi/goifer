from goifer import GoiferClient

# create a new client and call explain()
config = {
}
client = GoiferClient(config=config)

# get records for query
records = client.search(query='Zürich')

# display 5 records
print('')
print('First 5 results for `Zürich`')
for r in records[:5]:
    print("* ", r['title'])
