# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

*(NOTE: All examples use fictious data or freely available data sets.)*

## [0.16.0] - 2020-08-27

### Added

- Added most of remaining FSS entities:
  - AuditEvent
  - CarePlan
  - DiagnosticReport
  - DocumentReference
  - Encounter
  - ImagingStudy
  - Immunization
  - Media
  - MedicationAdministration
  - MedicationDispense
  - MedicationRequest
  - MedicationStatement
  - Person
  - Practitioner
  - Procedure
  - ProcedureRequest
  - Provenance
  - ReferralRequest
  - Sequence
  - Specimen
- Add abstract `Item` class for entities that don't relate to a patient (e.g. Organization and Practitioner)

### Changed

All date columns now return two columns--one for the local time (with time zone removed) and one for the time zone offset in hours. Consider the `onsetDateTime` column from BRCA's `Condition` table:

```
   onsetDateTime.tz       onsetDateTime.local
0               0.0 1998-01-01 00:00:00+00:00
1               0.0 2010-01-01 00:00:00+00:00
2               0.0 2008-01-01 00:00:00+00:00
3               0.0 1994-01-01 00:00:00+00:00
4               0.0 2008-01-01 00:00:00+00:00
5               0.0 2012-01-01 00:00:00+00:00
6               0.0 2017-06-27 04:00:00+00:00
```


## [0.15.0] - 2020-08-05

Includes more work on the easy modules (imported via `import phc.easy as phc`). 

### Added

- Added `phc.easy.Query.execute_ga4gh` that auto-scrolls GA4GH results
- Added `phc.easy.Sequence` as another entity module
- Added generic methods on `phc.easy.Query`
  - `get_count_by_field`
  - `get_codes`
  - `execute_composite_aggregations` (used by `get_count_by_field` and `get_codes`)
- Added `phc.easy.PatientItem.get_count_by_patient` (Observation, Procedure, Specimen, etc.)

```python
# Example: Get number of procedures by patient
phc.Procedure.get_count_by_patient()

#                                      doc_count
# subject.reference                              
# 518eb55d-adbf-42c3-8aed-68176d0ed4b7        334
# 67233488-ddd6-46e1-88cc-a93140b86c02       2088
# b41f8107-85e1-42c3-b36e-400085799ab5        176
```

- Added `phc.easy.PatientItem.get_count_by_field` (Observation, Procedure, Specimen, etc.)

```python
# Example: Get count of unique procedure display codes
phc.Procedure.get_count_by_field("code.coding.display")

#                      code.coding.display  doc_count
# 0                             lumpectomy        247
# 1            modified radical mastectomy        322
# 2                                  other        272
# 3                      simple mastectomy        200
```

- Added `phc.easy.PatientItem.get_codes` (Observation, Procedure, Specimen, etc.)

```python
# Example: Get observation codes for specific patients
phc.Observation.get_codes(patient_ids=[
    "e296f292-230f-444c-887f-0b213bde90fa",
    "78adf262-c77e-4cb3-8435-034bd9e73b64"
])

#    doc_count            system     code                                     display        field
# 0        1.0  http://loinc.org  21893-3  Regional lymph nodes positive [#] Specimen  code.coding
# 1        2.0  http://loinc.org  21975-8                        Date of Last Contact  code.coding
# 2        1.0  http://loinc.org  21981-6                 Date of Disease Progression  code.coding
# 3        2.0  http://loinc.org  49683-6                    HER2/neu receptor status  code.coding
# 4        2.0  http://loinc.org  63931-0                           Date of Diagnosis  code.coding
# 5        2.0  http://loinc.org  85337-4                    Estrogen Receptor Status  code.coding
```

### Changed

- Passing `log` to any PatientItem entities now logs the FSS query being run
- For aggregations, `phc.Query.execute_fhir_dsl` now returns a `FhirAggregation` if an aggregation is specified in the query
- `phc.Query.execute_fhir_dsl_with_options` now caches aggregation queries in JSON format
- Specifying `patient_id` and/or `patient_ids` is now properly supported with a custom FHIR query.

```python
# Example: Get observations tagged with loinc for a specific patient

phc.Observation.get_data_frame(patient_id="<id>", query_overrides={
    "where": {
        "type": "elasticsearch",
        "query": {
            "term": {
                "code.coding.system.keyword": "http://loinc.org"
            }
        }
    }
})
```


### Fixed

- Fix `phc.easy.Procedure` not inheriting new `phc.easy.PatientItem` behavior


## [0.14.1]  - 2020-07-15

### Fixed

- Fixed missing trust_env args in created client objects

## [0.14.0]  - 2020-07-14

### Added

- All-new easy module for faster analysis! Simply `import phc.easy as phc`.
- Add `Auth` for shared authentication details (account, project, and token)
- Add `Query` for scrolling through FHIR Search Service (FSS) data
- Add `Frame` for expanding columns that contain FHIR data and parsing dates
- Add `APICache` for auto-caching results from easy modules
- Add `CSVWriter` for intelligently writing batches O(1) without having memory grow
- Includes `Project`, `Patient`, `Observation`, `Procedure`, `Condition`,
  `Goal`, and `Specimen`

## [0.13.0]  - 2020-04-17

### Added

- Switched build over to github actions

## [0.12.3]  - 2020-04-13

### Added

- Adds `dsl` and `sql` methods to `phc.services.Fhir`

### Changed

- Deprecates `execute_sql` and `execute_es` methods in `phc.services.Fhir`

## [0.12.2]  - 2020-03-25

### Fixed

- Added retries to file download requests

## [0.12.1]  - 2020-03-25

### Fixed

- Fixed retry logic to include OS level errors.

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

[0.16.0]: https://github.com/lifeomic/phc-sdk-py/compare/v0.15.0...v0.16.0
[0.15.0]: https://github.com/lifeomic/phc-sdk-py/compare/v0.14.1...v0.15.0
[0.14.1]: https://github.com/lifeomic/phc-sdk-py/compare/v0.14.0...v0.14.1
[0.14.0]: https://github.com/lifeomic/phc-sdk-py/compare/v0.13.0...v0.14.0
[0.13.0]: https://github.com/lifeomic/phc-sdk-py/compare/v0.12.2...v0.13.0
[0.12.3]: https://github.com/lifeomic/phc-sdk-py/compare/v0.12.2...v0.12.3
[0.12.2]: https://github.com/lifeomic/phc-sdk-py/compare/v0.12.1...v0.12.2
[0.12.1]: https://github.com/lifeomic/phc-sdk-py/compare/v0.12.0...v0.12.1
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
