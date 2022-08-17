[![PyPI Version](https://img.shields.io/pypi/v/goifer)](https://pypi.org/project/goifer/)
[![Tests + Linting Python](https://github.com/metaodi/goifer/actions/workflows/lint_python.yml/badge.svg)](https://github.com/metaodi/goifer/actions/workflows/lint_python.yml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

<img src="https://user-images.githubusercontent.com/538415/184494773-c5523f26-bb97-405d-8d29-24a916e5978c.jpeg" alt="goifer logo" width="300" />

# goifer

**goifer** is the glue code needed to extract information from the Gever (Geschäftsverwaltungssystem) of the canton of Zurich.
It is a client for python to make requests to the [Gever API](https://www.zh.ch/de/politik-staat/opendata.html/details/709@kantonsrat-kanton-zuerich?keyword=ogd#/details/709@fachstelle-ogd-kanton-zuerich).

_goifer_ is Swiss German for spit/saliva, a pun on «Gever» and the «spit» needed to get something out of it.

## Table of Contents

* [Installation](#installation)
* [Usage](#usage)
* [Development](#development)
* [Release](#release)

## Installation

[goifer is available on PyPI](https://pypi.org/project/goifer/), so to install it simply use:

```
$ pip install goifer
```

## Usage

See the [`examples` directory](https://github.com/metaodi/goifer/tree/main/examples) for more scripts.

### `search`

`search` is used to query an index (i.e. entity) and get results.

```python
>>> import goifer
>>> result = goifer.search("canton_zurich", index="Wahlkreise", query="seq > 0")
>>> print(result)
SearchResponse(count=18, next_start_record=11)
>>> print(result.count)
18
>>> print(result[0])
{'obj_guid': '99221ca914ae43ab99935379dd4be037', 'seq': '2242327', 'idx': 'Wahlkreise', 'name': 'XIII Pfäffikon', 'nil': False, 'inaktiv': False}
```

The return value of `search` is iterable, so you can easily loop over it.
Or you can use indices to access elements, e.g. `result[1]` to get the second element, or `result[-1]` to get the last one.

Even [slicing](https://python-reference.readthedocs.io/en/latest/docs/brackets/slicing.html) is supported, so you can do things like only iterate over the first 5 elements using

```python
for records in records[:5]:
   print(record)
```

### `indexes`

To get a better idea of the available indexes, you can get all configured indexes with `indexes`:

```
>>> goifer.indexes('canton_zurich')
['Behoerden', 'SitzungenDetail', 'Geschaeft', 'Mitglieder', 'Parteien', 'Wahlkreise', 'Direktion', 'Geschaeftsart', 'Gremiumtyp', 'KRVersand', 'Ablaufschritt']
```

### `file`

Some indexes return a reference to a document (called `edokument` or `edocument`).
`goifer` generates a download URL for those documents:

```
>>> meetings = goifer.search("canton_zurich", "SitzungenDetail", "seq>0")
>>> meetings[0]['dokument']['edokument']
{'id': '9db1203429e04a39a233e56eab42feea-332', 'filename': '63. KR-Protokoll vom 9.7.2012, Nachmittag.pdf', 'version': {'nr': '1', 'rendition': {'extension': 'pdf', 'ansicht': 'PDF'}}, 'download_url': 'https://parlzhcdws.cmicloud.ch/parlzh3/cdws/Files/9db1203429e04a39a233e56eab42feea-332/1/PDF'}
```

The `download_url` can be used to download the file, the corresponding filename is in the `filename` field.

Sometimes you want to generate the download URL yourself, in these cases you can use the `file` method:

```
>>> import goifer
>>> client = goifer.client("canton_zurich")
>>> res = client.search("Mitglieder", "Name adj Marti and Vorname adj Res")[0]
>>> client.file("Mitglieder", res["foto_id"], res['foto_version']['nr'], 'Original')
'https://parlzhcdws.cmicloud.ch/parlzh2/cdws/Files/6bf54e3bdd24400d85e13169c3a5bbf8-1664/1/Original'
```

### `schema`

To know what fields are in a search result or to check with fields are available for queries (i.e. `searchfields`), use the `schema` method:

```
>>> s = goifer.schema('canton_zurich', 'Wahlkreise')
{'targetnamespace': 'http://www.cmiag.ch/cdws/Wahlkreise', 'elementformdefault': 'qualified', 'annotation': {'documentation': {'searchfield': [{'type': 'SearchFieldBoolean', 'Name': 'inaktiv', 'BoostFactor': '1', 'Nrs': '6'}, {'type': 'SearchFieldText', 'Name': 'Name', 'BoostFactor': '1', 'Nrs': '5'}]}}, 'complextype': {'name': 'Wahlkreis', 'sequence': {'element': [{'name': 'Name', 'type': 'xsd:string'}, {'name': 'inaktiv', 'type': 'xsd:boolean', 'nillable': 'true'}]}, 'attribute': [{'name': 'OBJ_GUID', 'type': 'xsd:string', 'use': 'required'}, {'name': 'SEQ', 'type': 'xsd:string', 'use': 'optional'}, {'name': 'IDX', 'type': 'xsd:string', 'use': 'optional'}]}, 'element': {'name': 'Wahlkreis', 'type': 'Wahlkreis'}}
```

## Development

To develop on this project, install `flit`:

```
pip install flit
flit install -s
```

Or use the provided `dev_setup.sh` script.

To contribute to goifer simply clone this repository and follow the instructions in [CONTRIBUTING.md](/CONTRIBUTING.md).

This project has a Makefile with the most common commands.
Type `make help` to get an overview.

## Release

To create a new release, follow these steps (please respect [Semantic Versioning](http://semver.org/)):

1. Adapt the version number in `goifer/__init__.py`
1. Update the CHANGELOG with the version
1. Create a pull request to merge `develop` into `main` (make sure the tests pass!)
1. Create a [new release/tag on GitHub](https://github.com/metaodi/goifer/releases) (on the main branch)
1. The [publication on PyPI](https://pypi.python.org/pypi/goifer) happens via [GitHub Actions](https://github.com/metaodi/goifer/actions?query=workflow%3A%22Upload+Python+Package%22) on every tagged commit
