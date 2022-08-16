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

# get factions
factions = client.search("Behoerden", query="GremiumTyp adj Fraktion")

for faction in factions:
    print_header(f"Fraktion: {faction['name']}")
    dump(faction)

    # get members of faction
    print_title("Mitglieder:")
    members = client.search(
        "Mitglieder",
        query=f"dauer_end >= \"2020-11-19 00:00:00\" and dauer_start <= \"2020-11-19 00:00:00\" and gremium adj {faction['kurzname']} sortBy name/sort.ascending vorname/sort.ascending",
    )

    name_members = [f"{m['name']}, {m['vorname'] or ''} ({m['ort']})" for m in members]
    dump(name_members)
