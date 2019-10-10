# phc-sdk-py

The phc-sdk-py is a developer kit for interfacing with the PHC API on Python 3.6 and above.

## Table of contents

1. [Project Status](#project-status)
1. [Getting Started](#getting-started)
    1. [Dependencies](#dependencies)
    1. [Getting the Source](#getting-the-source)
    1. [Development](#development)
    1. [Installation](#installation)
    1. [Usage](#usage)
1. [Release Process](#release-process)
    1. [Versioning](#versioning)
1. [Contributing](#contributing)
1. [License](#license)
1. [Authors](#authors)
1. [Acknowledgements](#acknowledgements)


# Project Status

![GitHub](https://img.shields.io/github/license/lifeomic/phc-sdk-py.svg?style=for-the-badge)
![Travis (.org) branch](https://img.shields.io/travis/lifeomic/phc-sdk-py/master.svg?style=for-the-badge)
![PyPI status](https://img.shields.io/pypi/status/phc.svg?style=for-the-badge)
![GitHub release](https://img.shields.io/github/release/lifeomic/phc-sdk-py.svg?style=for-the-badge)

**[Back to top](#table-of-contents)**

# Getting Started

## Dependencies

* [Python 3](https://www.python.org/download/releases/3.0/) version >= 3.7

## Getting the Source

This project is [hosted on GitHub](https://github.com/lifeomic/phc-sdk-py). You can clone this project directly using this command:

```bash
git clone git@github.com:lifeomic/phc-sdk-py.git
```
**[Back to top](#table-of-contents)**

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

**[Back to top](#table-of-contents)**

## Installation

```bash
pip3 install phc
```
**[Back to top](#table-of-contents)**

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


**[Back to top](#table-of-contents)**

# Release Process

[Releases](https://github.com/lifeomic/phc-sdk-py/releases) are generally created with each merged PR. Packages for each release are published to [PyPi](https://pypi.org/project/phc/). See [CHANGELOG.md](CHANGELOG.md) for release notes.

## Versioning

This project uses [Semantic Versioning](http://semver.org/).

**[Back to top](#table-of-contents)**


# Contributing

We encourage public contributions! Please review [CONTRIBUTING.md](CONTRIBUTING.md) and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for details on our code of conduct and development process.

**[Back to top](#table-of-contents)**


# License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

**[Back to top](#table-of-contents)**


# Authors

See the list of [contributors](https://github.com/lifeomic/cli/contributors) who participate in this project.

**[Back to top](#table-of-contents)**


# Acknowledgements

This project is built with the following:

* [aiohttp](https://aiohttp.readthedocs.io/en/stable/) - Asynchronous HTTP Client/Server for asyncio and Python.

**[Back to top](#table-of-contents)**