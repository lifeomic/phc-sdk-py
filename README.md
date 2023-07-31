# PHC SDK for Python

The phc-sdk-py is a developer kit for interfacing with the [PHC API](https://api.docs.lifeomic.com/) on Python 3.7 and above.

## Project Status

![GitHub](https://img.shields.io/github/license/lifeomic/phc-sdk-py.svg?style=for-the-badge)
![PyPI status](https://img.shields.io/pypi/status/phc.svg?style=for-the-badge)
![Downloads](https://img.shields.io/pypi/dw/phc?style=for-the-badge)
![GitHub release](https://img.shields.io/github/release/lifeomic/phc-sdk-py.svg?style=for-the-badge)
[![Docs](https://img.shields.io/badge/DOCS-PASSING-green?style=for-the-badge)](https://lifeomic.github.io/phc-sdk-py/)
[![User Guides](https://img.shields.io/badge/DOCS-PASSING-green?style=for-the-badge)](https://devcenter.docs.lifeomic.com/guides/python-sdk)

## Getting Started

### Dependencies

- [Python 3](https://www.python.org/download/releases/3.0/) version >= 3.8

### Getting the Source

This project is [hosted on GitHub](https://github.com/lifeomic/phc-sdk-py).

### Usage

A `Session` needs to be created first that stores the token and account information needed to access the PHC API. One can currently using API Key tokens generated from the PHC Account, or OAuth tokens generated using the [CLI](https://github.com/lifeomic/cli).

```python
from phc import Session

session = Session(token=<TOKEN VALUE>, account="myaccount")
```

Once a `Session` is created, you can then access the different parts of the platform.

```python
from phc.services import Accounts

accounts = Accounts(session)
myaccounts = accounts.get_list()
```

## Contributing

We encourage public contributions! Please review [CONTRIBUTING.md](CONTRIBUTING.md) and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for details on our code of conduct and development process.

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## Authors

See the list of [contributors](https://github.com/lifeomic/phc-sdk-py/contributors) who participate in this project.

## Acknowledgements

This project is built with the following:

- [aiohttp](https://aiohttp.readthedocs.io/en/stable/) - Asynchronous HTTP Client/Server for asyncio and Python.
