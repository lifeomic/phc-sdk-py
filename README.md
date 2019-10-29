The phc-sdk-py is a developer kit for interfacing with the PHC API on Python 3.6 and above.

# Project Status

![GitHub](https://img.shields.io/github/license/lifeomic/phc-sdk-py.svg?style=for-the-badge)
![Travis (.org) branch](https://img.shields.io/travis/lifeomic/phc-sdk-py/master.svg?style=for-the-badge)
![PyPI status](https://img.shields.io/pypi/status/phc.svg?style=for-the-badge)
![GitHub release](https://img.shields.io/github/release/lifeomic/phc-sdk-py.svg?style=for-the-badge)

# Getting Started

## Dependencies

* [Python 3](https://www.python.org/download/releases/3.0/) version >= 3.7

## Getting the Source

This project is [hosted on GitHub](https://github.com/lifeomic/phc-sdk-py). You can clone this project directly using this command:

```bash
git clone git@github.com:lifeomic/phc-sdk-py.git
```

## Development

Python environments are managed using [virtualenv](https://virtualenv.pypa.io/en/latest/).  Be sure to have this installed first `pip install virtualenv`.  The makefile will setup the environment for the targets listed below.


### Setup

This installs some pre-commit hooks that will format and lint new changes.

```bash
make setup
```

### Running tests

```bash
make test
```

### Linting

```bash
make lint
```

## Installation

```bash
pip3 install phc
```
## Usage

A `Session` needs to be created first that stores the token and account information needed to access the PHC API.  One can currently using API Key tokens generated from the PHC Account, or OAuth tokens generated using the [CLI](https://github.com/lifeomic/cli).

```python
from phc import Session

session = Session(token=<TOKEN VALUE>, account="myaccount")
```

Once a `Session` is created, you can then access the different parts of the platform.

```python
from phc import Accounts

accounts = Accounts(session)
myaccounts = accounts.get_list()
```

Here's and example of fetching FHIR resource using SQL:
```python
import pandas as pd
from phc import Fhir

fhir = Fhir(session)

res = fhir.execute_sql(project='19e34782-91c4-4143-aaee-2ba81ed0b206',
                       statement='SELECT * from patient LIMIT 0,5000')

resources = list(map(lambda r: r.get("_source"), res.get("hits").get("hits")))
df = pd.DataFrame(resources)
```

While here's an example of fetching patients observation data from using Analytics DSL. Notice that in this case, there is a helper query builder class (PatientFilterQueryBuilder):

```python
from phc import Analytics, PatientFilterQueryBuilder

client = Analytics(session)
search = PatientFilterQueryBuilder()
search.patient() \
    .observations() \
    .code(eq='11142-7') \
    .system(eq='http://loinc.org') \
    .value_quantity(lt=40)

res = client.get_patients(project='5a07dedb-fa2a-4cb0-b662-95b23a050221', query_builder=search)

print(f"Found {len(res)} patients")

```

While here's an example of fetching data using data lake engine:

```python
from phc import Session, DataLakeQuery, Analytics

session = Session()
client = Analytics(session)

dataset_id = '19e34782-91c4-4143-aaee-2ba81ed0b206'
query_string = "SELECT sample_id, gene, impact, amino_acid_change, histology FROM variant WHERE tumor_site='breast'"
output_file_name = 'query-test-notebook'
query = DataLakeQuery(dataset_id=dataset_id, query=query_string, output_file_name=output_file_name)

query_id = client.execute_data_lake_query(query)
specific_query = client.get_data_lake_query(query_id)
paginated_dataset_queries = client.list_data_lake_queries(dataset_id=dataset_id)
print(query_id)
```

# Release Process

[Releases](https://github.com/lifeomic/phc-sdk-py/releases) are generally created with each merged PR. Packages for each release are published to [PyPi](https://pypi.org/project/phc/). See [CHANGELOG.md](CHANGELOG.md) for release notes.

## Versioning

This project uses [Semantic Versioning](http://semver.org/).


# Contributing

We encourage public contributions! Please review [CONTRIBUTING.md](CONTRIBUTING.md) and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for details on our code of conduct and development process.


# License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.


# Authors

See the list of [contributors](https://github.com/lifeomic/cli/contributors) who participate in this project.


# Acknowledgements

This project is built with the following:

* [aiohttp](https://aiohttp.readthedocs.io/en/stable/) - Asynchronous HTTP Client/Server for asyncio and Python.
