# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.8.0]  - 2019-11-25

### Added

- Added `Analytics.list_data_lake_schemas` to fetch the schemas of each data lake table.
- Added `Analytics.get_data_lake_schema` to fetch the schema of a single data lake table.
- Added `Analytics.execute_data_lake_query_to_dataframe` to execute a data lake query and load the results to a Pandas dataframe.
- Added `Analytics.load_data_lake_result_to_dataframe` to load the results of a previously executed data lake query to a Pandas dataframe.
- Added `Files.exists` to check if a file exists.

## [0.7.0]  - 2019-11-20

### Added

- Added optional `pandas` setup install
- Added `ApiResponse.get_as_dataframe` to return a response item as a Pandas DataFrame.

## [0.6.0]  - 2019-11-01

### Added

- Added the `phc.services.Files` submodule that provides actions for files in PHC projects.
- Added the `phc.services.Cohorts` submodule that provides actions for files in PHC cohorts.
