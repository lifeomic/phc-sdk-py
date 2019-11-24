# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.7.1]  - 2019-11-21

### Fixed

- Fixed issue with `Files.download` to create target directories if they do not exist.

## [0.7.0]  - 2019-11-20

### Added

- Added optional `pandas` setup install
- Added `ApiResponse.get_as_dataframe` to return a response item as a Pandas DataFrame.

## [0.6.0]  - 2019-11-01

### Added

- Added the `phc.services.Files` submodule that provides actions for files in PHC projects.
- Added the `phc.services.Cohorts` submodule that provides actions for files in PHC cohorts.

[0.7.1]: https://github.com/lifeomic/phc-sdk-py/compare/v0.7.0...v0.7.1
[0.7.0]: https://github.com/lifeomic/phc-sdk-py/compare/v0.6.0...v0.7.0
[0.6.0]: https://github.com/lifeomic/phc-sdk-py/compare/v0.5.0...v0.6.0
