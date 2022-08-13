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

See the [`examples` directory](https://github.com/metaodi/goifer/tree/master/examples) for more scripts.

### `search`

```python
>>> import goifer
>>> records = goifer.search('canton_zurich', index='Mitglieder' query='Marti')
>>> print(records)
SearchResponse(count=17,next_start_record=11)
>>> print(records.count)
4
```


```
import goifer

api = "https://parlzhcdws.cmicloud.ch/parlzh2/cdws/Index/"
api = "https://www.integ.gemeinderat-zuerich.ch/api"



goifer.get_indexes()[:5]
file = goifer.get_file(id="123asdasd")
result = goifer.search(index="Geschaeft", cql="
```

The return value of `search` is iterable, so you can easily loop over it. Or you can use indices to access elements, e.g. `records[1]` to get the second elemenet, or `records[-1]` to get the last one.

Even [slicing](https://python-reference.readthedocs.io/en/latest/docs/brackets/slicing.html) is supported, so you can do things like only iterate over the first 5 elements using

```python
for records in records[:5]:
   print(record)
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
