# make sure you have termcolor and PyYAML installed: pip install termcolor pyyaml
import goifer
from termcolor import cprint
import yaml


def print_header(s):
    cprint(s, "green", attrs=["bold"])


def print_title(s):
    cprint(s, attrs=["bold"])


def dump(d):
    print(yaml.dump(d, allow_unicode=True, default_flow_style=False))


client = goifer.Client("canton_zurich")

print_title("Indexes:")
indexes = client.indexes()
dump(indexes)

# loop over all indexes
for index in indexes:
    print_header(index)
    records = client.search(index, query="seq > 0")
    print("")

    # print first record of each index
    dump(records[0])
    print("")
