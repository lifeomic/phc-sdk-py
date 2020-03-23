# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.12.0]  - 2020-03-23

### Added

- Added retry support for failed API requests.

## [0.11.0]  - 2020-03-17

### Added

- Added the `trust_env` parameter to all service classes to enable http proxy support.

## [0.10.0]  - 2020-03-10

### Added

- Added `execute_sql` to `phc.services.Analytics`.

## [0.9.2]  - 2020-02-19

### Added

- Added scroll support to `phc.services.Fhir` via the `scroll` param.

## [0.9.1]  - 2019-12-17

### Changed

- Fixed `phc.services.Genomics.Status` enum.

## [0.9.0]  - 2019-12-16

### Changed

- Added `phc.services.Genomics` for performing genomic related operations.

## [0.8.1]  - 2019-11-27

### Changed

- In `Analytics.load_data_lake_result_to_dataframe` increased the amount of time it takes to wait for a results file.

## [0.8.0]  - 2019-11-25

### Added

- Added `Analytics.list_data_lake_schemas` to fetch the schemas of each data lake table.
- Added `Analytics.get_data_lake_schema` to fetch the schema of a single data lake table.
- Added `Analytics.execute_data_lake_query_to_dataframe` to execute a data lake query and load the results to a Pandas dataframe.
- Added `Analytics.load_data_lake_result_to_dataframe` to load the results of a previously executed data lake query to a Pandas dataframe.
- Added `Files.exists` to check if a file exists.

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

[0.12.0]: https://github.com/lifeomic/phc-sdk-py/compare/v0.11.0...v0.12.0
[0.11.0]: https://github.com/lifeomic/phc-sdk-py/compare/v0.10.0...v0.11.0
[0.10.0]: https://github.com/lifeomic/phc-sdk-py/compare/v0.9.2...v0.10.0
[0.9.2]: https://github.com/lifeomic/phc-sdk-py/compare/v0.9.1...v0.9.2
[0.9.1]: https://github.com/lifeomic/phc-sdk-py/compare/v0.9.0...v0.9.1
[0.9.0]: https://github.com/lifeomic/phc-sdk-py/compare/v0.8.1...v0.9.0
[0.8.1]: https://github.com/lifeomic/phc-sdk-py/compare/v0.8.0...v0.8.1
[0.8.0]: https://github.com/lifeomic/phc-sdk-py/compare/v0.7.1...v0.8.0
[0.7.1]: https://github.com/lifeomic/phc-sdk-py/compare/v0.7.0...v0.7.1
[0.7.0]: https://github.com/lifeomic/phc-sdk-py/compare/v0.6.0...v0.7.0
[0.6.0]: https://github.com/lifeomic/phc-sdk-py/compare/v0.5.0...v0.6.0
