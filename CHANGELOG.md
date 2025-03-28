# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

_(NOTE: All examples use fictitious data or freely available data sets.)_

## [1.1.0] - 2025-03-20

### Added

- Added `get_token()` method to `phc.services.Agents` API client to retrieve a
temporary token for accessing LLM functionality.

## [1.0.0] - 2024-12-17

### Removed

- Support for Python 3.8 has been dropped, since 3.8 has reached end-of-life:
  https://devguide.python.org/versions/

### Changed

- This project now uses `pydantic` v2 instead of v1.
- **BREAKING**: `PagingApiOptions.dict()` has been renamed to
  `PagingApiOptions.model_dump()`.

## [0.36.0] - 2024-11-15

### Added

- Added a new `phc.services.Agents` API client with an `invoke_basic` method for
  invoking a basic multi-modal LLM.

## [0.35.0] - 2024-05-29

### Added

- Updated `phc.services.patient_ml.PatientML` API client to the latest version.

## [0.34.1] - 2024-03-13

### Fixed

- the `params` argument in `phc.services.Fhir#es_sql()` is optional.

## [0.34.0] - 2024-03-13

### Added

- A New function `es_sql()` to `phc.services.Fhir` class to execute OpenSearch
  SQL.

Example:

```python
df = Fhir(session).es_sql(
    project_id='xxx',
    statement='SELECT id, subject.reference FROM diagnostic_report WHERE identifier.system = ? LIMIT 10',
    params=[{
      "type": "string",
      "value": "example-identifier-system"
    }]
).get_as_dataframe('datarows')
```

## [0.33.4] - 2023-11-02

### Fixed

- The `phc.services.PatientML` API client will now ignore extra values, instead
  of throwing an error if one is found when parsing an entity.

## [0.33.0] - 2023-07-28

### Added

- Runs on Python 3.8+

### Removed

- Python 3.7 is no longer supported.

## [0.32.0] - 2023-07-20

### Added

- The `phc.services.PatientML` API client is now fully typed. Request bodies,
  response bodies, and query parameters now allow for static type checking, and
  are runtime type-checked as well.

## [0.31.0] - 2023-07-18

### Fixed

- Pinned the major versions of the package's dependencies, so untested breaking
  changes are excluded from the package's installation
- Removed dev dependencies that were already specified as package dependencies
- Pinned the exact version of the dev dependencies, to improve CI/CD determinism

## [0.29.0] - 2023-06-22

### Added

- Added new `phc.services.PatientML` API client which can be used to call the
  LifeOmic Patient ML Service API.

## [0.23.2] - 2021-09-27

### Fixed

- Terms and any list parameters (e.g. `ids`/`patient_ids`) with more than 30K
  values get auto-chunked into multiple queries (No need to iterate!)

### Added

- Added support for single/multiple values with the `term` or `terms` (New!)
  parameters
- Added configurable term limit for sending multiple queries (param `max_terms`)
- Added `phc.DataLake` for sending SQL queries to the data lake

Example

```python
phc.DataLake.get_data_frame(
  "SELECT * FROM my_table",
  extension="parquet",
  transform=lambda df: df.drop(["id"], axis=1)
)
# => Loading from "~/Downloads/phc/api-cache/data_lake_my_table_f84bab09.parquet"
```

## [0.23.1] - 2021-07-26

### Fixed

- Fix import error because of missing `__init__` file for summary API folder

## [0.23.0] - 2021-07-23

### Fixed

- `phc.Project` now operates properly when one of the accounts only has limited
  access
- `phc.Observation`, `phc.Condition`, and `phc.Procedures`'s `get_codes` method
  now uses the new summary APIs to return better results.

### Added

- Summary APIs ([PR #150](https://github.com/lifeomic/phc-sdk-py/pull/150))
  - `phc.SummaryClinicalCounts` - Retrieve all clinical counts (across tables
    like observation, conditions, procedures, and medications)
  - `phc.SummaryOmicsCounts` - Retrieve summaries across genomic data (counts of
    clinvar_significance, gene_variant, sequence, test, etc)
  - `phc.SummaryCounts` - Retrieve all summaries (across omics and clinical)
  - `phc.SummaryItemCounts` - Retrieve counts for a specific table (e.g.
    `condition`, `procedure`)

Example

```python
phc.SummaryClinicalCounts.get_data_frame(match="fuzzy", system=["snomed.info", "loinc.org"])
#        summary       code                           display  patient_count                  system   count media_type  media_type_count
# 0    procedure  406505007       modified radical mastectomy          322.0  http://snomed.info/sct   322.0        NaN               NaN
# 1    procedure  392090004                             other          272.0  http://snomed.info/sct   272.0        NaN               NaN
# 2  observation    21975-8              Date of Last Contact         1094.0        http://loinc.org  1094.0        NaN               NaN
# 3   medication  387420009                           cytoxan          514.0  http://snomed.info/sct   523.0        NaN               NaN
# 4   medication  372817009       doxorubicin+cyclophosphamid          364.0  http://snomed.info/sct   371.0        NaN               NaN
# 5    condition  254837009                              None         1086.0  http://snomed.info/sct  1086.0        NaN               NaN
# 6    condition   82711006  Infiltrating duct carcinoma, NOS          778.0  http://snomed.info/sct   778.0        NaN               NaN
```

## [0.22.2] - 2021-04-30

### Fixed

- Make token optional when using a custom adapter that doesn't support
  refreshing the token

## [0.22.1] - 2021-04-27

### Added

- Added ability to use custom adapter for sending/receiving underlying data
  (e.g. for tests)

## [0.22.0] - 2021-03-24

### Fixed

- Bug that caused error related to printing progress

### Added

Added lots of Ocr functionality and a Composition module in the `easy`
namespace.

- `phc.Ocr.Config` - Create and update PrecisionOCR config within a project
- `phc.Ocr.Document` - Retrieve PrecisionOCR documents
- `phc.Ocr.DocumentComposition` - Retrieve metadata by page for PrecisionOCR
  documents
- `phc.Ocr.Block` - Retrieve the text and layout metadata from a PrecisionOCR
  document
- `phc.Ocr.Suggestion` - Retrieve all permutations of PrecisionOCR medical
  suggestions
- `phc.Composition` - Base FHIR class for retrieving Composition resources from
  the FHIR Search Service

Added the ability to create, read, update, and delete using the FHIR DSTU3 API
by appending `.DSTU3` to any easy module that supports it.

```python
phc.Patient.DSTU3.create(...)
phc.Patient.DSTU3.get(...)
phc.Patient.DSTU3.update(...)
phc.Patient.DSTU3.put(...)
phc.Patient.DSTU3.delete(...)
```

## [0.21.1] - 2020-12-17

### Fixed

- Updated API calls to the data-lake to use correct endpoints.

## [0.21.0] - 2020-12-10

### Added

- `Tools` - A service to manager resources in the tool registry service

  - `tools.create` - Adds a tool to the registry
  - `tools.download` - Downloads a tool
  - `tools.get` - Gets the default verson or a specific version of a tool
  - `tools.add_version` - Adds a verson to an existing tool
  - `tools.delete` - Deletes the tool or a specific version of a tool
  - `tools.get_list` - Returns tools from the registry and allows for optional
    filters

- `Workflows` - A service to manager workflows

  - `workflows.run` - Runs a workflow using a provided tool from the registry
  - `workflows.get` - Gets a workflow run
  - `workflows.get_list` - Returns all workflows for a project
  - `workflows.describe` - Returns a list of the inputs and types the workflow
    requires to run a tool

- Added filtering by id for all `phc.easy` modules

```python
# By single ID
phc.Patient.get_data_frame(id="<value>")

# Or by multiple IDs
phc.Observation.get_data_frame(ids=["<value1>", "<value2>"])
```

- Added getting all pages of results for `phc.Project`

### Fixed

- Genomics modules (`phc.easy`) now handle an out of range date via a warning
  (and auto-conversion to `NaT`)
- Setting and retrieving projects now works properly again (Previously, projects
  were inaccurate or sometimes missing.)

## [0.20.0] - 2020-11-19

### Added

- Auto-retrieve GenomicTests for each type of variant (short, copy number,
  structural, and expression) if no `variant_set_ids` passed

```python
# Specify the specific sets within a test
phc.GenomicShortVariant.get_data_frame(variant_set_ids)

# ...or have it auto-fetch the relevant tests (uses a sample if executed with
# no arguments)
phc.GenomicShortVariant.get_data_frame()
```

- Added `GenomicExpression`

```python
phc.GenomicExpression.get_data_frame(
    expression=">=4000",
    gene=["B2M", "MIR663B", "MT-CYB"],
    order_by="expression:desc",
    in_ckb=True,
    all_results=True,
    log=True
)
```

- Added `GenomicCopyNumberVariant`

```python
phc.GenomicCopyNumberVariant.get_data_frame(
    effect=[phc.Option.CopyNumberStatus.AMPLIFICATION],
    in_ckb=True
)
```

- Added `GenomicStructuralVariant`

```python
phc.GenomicStructuralVariant.get_data_frame(
    patient_id="2c8660b4-1e63-403e-b52b-55c290072a66",
    effect=[phc.Option.StructuralType.TRANSLOCATION],
    gene=["TNRC6B", "CTD-2616J11.4"],
    max_pages=2,
    page_size=100
)
```

- Added `Gene` and `GeneClass` from the knowledge APIs

```python
phc.Gene.get_data_frame()
phc.GeneSet.get_data_frame()
```

- Added abstract class `GenomicVariant` from which these specific classes
  inherit

- Added a whole host of options for these variant/expression classes

  - phc.Option.Chromosome
  - phc.Option.ClinVarReview
  - phc.Option.ClinvarSignificance
  - phc.Option.CodingEffect
  - phc.Option.Common
  - phc.Option.CopyNumberStatus
  - phc.Option.GeneClass
  - phc.Option.Zygosity

- Added run-time validation of variant/expression options using these classes

  - phc.easy.omics.option.genomic_copy_number_variant.GenomicCopyNumberVariant
  - phc.easy.omics.option.genomic_expression.GenomicExpression
  - phc.easy.omics.option.genomic_short_variant.GenomicShortVariant
  - phc.easy.omics.option.genomic_structural_variant.GenomicStructuralVariant
  - phc.easy.omics.option.genomic_test.GenomicTest

### Changed

- Updated options for `GenomicShortVariant`

```python
phc.GenomicShortVariant.get_data_frame(
    patient_id="2c8660b4-1e63-403e-b52b-55c290072a66",
    chromosome=[phc.Option.Chromosome.CHR_19],
    gene_class=[phc.Option.GeneClass.PROTEIN_CODING],
    zygosity=[phc.Option.Zygosity.HETEROZYGOUS],
    rs_id=["rs11324363", "rs36247", "rs77134098"],
    min_allele_frequency="0.2-1",
    log=True,
    all_results=True
)
```

## [0.19.0] - 2020-10-23

### Added

- Added `GenomicTest` and `GenomicShortVariant`

```python
# Get genomic tests and the associated sets
set_ids = phc.GenomicTest.get_data_frame(
    patient_id="8cb82aa0-7f2c-4fdb-bf91-0ed1b315392c",
    status="ACTIVE",
    test_type="shortVariant",
    all_results=True,
).id.values.tolist()

# Pull first 1000 short variants on chr1
phc.GenomicShortVariant.get_data_frame(
    variant_set_ids=set_ids,
    chromosome=["chr1"],
    page_size=1000,
    log=True
)
```

- Added filtering by exact code, system, and/or display

```python
phc.Condition.get_data_frame(code=["25910003", "30156004"], system="http://snomed.info/sct")
```

### Fixed

- Sped up finding projects - `phc.Project.set_current()`

### Changed

- Overhauled `get_codes` to make results more accurate and allow searching by
  display (See [#93](https://github.com/lifeomic/phc-sdk-py/pull/93) for full
  discussion)

```python
# 1. Get display values and number of records they occur in
phc.Observation.get_codes()
# =>    doc_count                       display                        field
# => 0      1094.0          Date of Last Contact                  code.coding
# => ...

# 2. Get full code values that match this text (case-insensitive)
phc.Observation.get_codes(display_query="date of")
# ...
# Retrieved 2332/2394 results
#
# =>           field            system     code                      display     doc_count
# =>  0  code.coding  http://loinc.org  63931-0            Date of Diagnosis       1094.0
# =>  1  code.coding  http://loinc.org  21975-8         Date of Last Contact       1094.0
# =>  2  code.coding  http://loinc.org  21981-6  Date of Disease Progression        144.0

# 3. Get full code values but restrict number of records to find the associated system and code
phc.Observation.get_codes("status", sample_size=10)
# ...
# Retrieved 10/3017 results
# Records with missing system/code values were not retrieved.

# =>           field     code            system                       display     doc_count
# =>  0  code.coding  85337-4  http://loinc.org      Estrogen Receptor Status        1048.0
# =>  1  code.coding  85339-0  http://loinc.org  Progesterone Receptor Status        1047.0
# =>  2          NaN      NaN               NaN      HER2/neu receptor status         919.0
# =>  3          NaN      NaN               NaN                    TMB Status           3.0
```

## [0.18.1] - 2020-10-09

### Fixed

- Fixed `Genomics.update_set` use of readgroupsets API

## [0.18.0] - 2020-10-09

### Added

- Added `Genomics.update_set` method for updating genomic sets

## [0.17.1] - 2020-09-17

### Added

- Paging requests with `all_results=True` now automatically retries to the
  server with an exponentially smaller batch size on error (`pow(limit, 0.85)`).
  We can't tell what the error is, but we can retry with a smaller page size.
- Added `page_size` to the easy modules for a custom batch size
- Added `max_pages` to the easy modules for capping the number of pages returned
- Added pretty print to FHIR Search Service queries when passing `log=True`
- Warn and convert out of range date times (e.g. `0217-01-01`) to `NaT`

### Fixed

- Properly parse date columns with positive time zones into the local time and
  time zone
- Resolved a `KeyError` issue with `coding` where the `valueCodeableConcept`
  didn't have a system or url
- Passing `patient_id` / `patient_ids` with a `must` FHIR Search Service query
  now works as expected

### Changed

[BREAKING] The expanded columns have changed to more reflect the location of the
value. All systems and URLs are separated by `__` and prefixed with either `url`
or `system`. Here is an example:

```python
input_dict = [
    {
        "url": "http://hl7.org/fhir/StructureDefinition/us-core-race",
        "valueCodeableConcept": {
            "text": "race",
            "coding": [
                {
                    "code": "2106-3",
                    "system": "http://hl7.org/fhir/v3/Race",
                    "display": "white",
                }
            ],
        },
    },
    {
        "url": "http://hl7.org/fhir/StructureDefinition/us-core-ethnicity",
        "valueCodeableConcept": {
            "text": "ethnicity",
            "coding": [
                {
                    "code": "2186-5",
                    "system": "http://hl7.org/fhir/v3/Ethnicity",
                    "display": "not hispanic or latino",
                }
            ],
        },
    },
]

assert generic_codeable_to_dict(input_dict) == {
    "url__hl7.org/fhir/StructureDefinition/us-core-race__valueCodeableConcept_text": "race",
    "url__hl7.org/fhir/StructureDefinition/us-core-race__valueCodeableConcept_coding_system__hl7.org/fhir/v3/Race__code": "2106-3",
    "url__hl7.org/fhir/StructureDefinition/us-core-race__valueCodeableConcept_coding_system__hl7.org/fhir/v3/Race__display": "white",
    "url__hl7.org/fhir/StructureDefinition/us-core-ethnicity__valueCodeableConcept_text": "ethnicity",
    "url__hl7.org/fhir/StructureDefinition/us-core-ethnicity__valueCodeableConcept_coding_system__hl7.org/fhir/v3/Ethnicity__code": "2186-5",
    "url__hl7.org/fhir/StructureDefinition/us-core-ethnicity__valueCodeableConcept_coding_system__hl7.org/fhir/v3/Ethnicity__display": "not hispanic or latino",
}
```

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
- Add abstract `Item` class for entities that don't relate to a patient (e.g.
  Organization and Practitioner)

### Changed

All date columns now return two columns--one for the local time (with time zone
removed) and one for the time zone offset in hours. Consider the `onsetDateTime`
column from BRCA's `Condition` table:

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
  - `execute_composite_aggregations` (used by `get_count_by_field` and
    `get_codes`)
- Added `phc.easy.PatientItem.get_count_by_patient` (Observation, Procedure,
  Specimen, etc.)

```python
# Example: Get number of procedures by patient
phc.Procedure.get_count_by_patient()

#                                      doc_count
# subject.reference
# 518eb55d-adbf-42c3-8aed-68176d0ed4b7        334
# 67233488-ddd6-46e1-88cc-a93140b86c02       2088
# b41f8107-85e1-42c3-b36e-400085799ab5        176
```

- Added `phc.easy.PatientItem.get_count_by_field` (Observation, Procedure,
  Specimen, etc.)

```python
# Example: Get count of unique procedure display codes
phc.Procedure.get_count_by_field("code.coding.display")

#                      code.coding.display  doc_count
# 0                             lumpectomy        247
# 1            modified radical mastectomy        322
# 2                                  other        272
# 3                      simple mastectomy        200
```

- Added `phc.easy.PatientItem.get_codes` (Observation, Procedure, Specimen,
  etc.)

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
- For aggregations, `phc.Query.execute_fhir_dsl` now returns a `FhirAggregation`
  if an aggregation is specified in the query
- `phc.Query.execute_fhir_dsl_with_options` now caches aggregation queries in
  JSON format
- Specifying `patient_id` and/or `patient_ids` is now properly supported with a
  custom FHIR query.

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

## [0.14.1] - 2020-07-15

### Fixed

- Fixed missing trust_env args in created client objects

## [0.14.0] - 2020-07-14

### Added

- All-new easy module for faster analysis! Simply `import phc.easy as phc`.
- Add `Auth` for shared authentication details (account, project, and token)
- Add `Query` for scrolling through FHIR Search Service (FSS) data
- Add `Frame` for expanding columns that contain FHIR data and parsing dates
- Add `APICache` for auto-caching results from easy modules
- Add `CSVWriter` for intelligently writing batches O(1) without having memory
  grow
- Includes `Project`, `Patient`, `Observation`, `Procedure`, `Condition`,
  `Goal`, and `Specimen`

## [0.13.0] - 2020-04-17

### Added

- Switched build over to github actions

## [0.12.3] - 2020-04-13

### Added

- Adds `dsl` and `sql` methods to `phc.services.Fhir`

### Changed

- Deprecates `execute_sql` and `execute_es` methods in `phc.services.Fhir`

## [0.12.2] - 2020-03-25

### Fixed

- Added retries to file download requests

## [0.12.1] - 2020-03-25

### Fixed

- Fixed retry logic to include OS level errors.

## [0.12.0] - 2020-03-23

### Added

- Added retry support for failed API requests.

## [0.11.0] - 2020-03-17

### Added

- Added the `trust_env` parameter to all service classes to enable http proxy
  support.

## [0.10.0] - 2020-03-10

### Added

- Added `execute_sql` to `phc.services.Analytics`.

## [0.9.2] - 2020-02-19

### Added

- Added scroll support to `phc.services.Fhir` via the `scroll` param.

## [0.9.1] - 2019-12-17

### Changed

- Fixed `phc.services.Genomics.Status` enum.

## [0.9.0] - 2019-12-16

### Changed

- Added `phc.services.Genomics` for performing genomic related operations.

## [0.8.1] - 2019-11-27

### Changed

- In `Analytics.load_data_lake_result_to_dataframe` increased the amount of time
  it takes to wait for a results file.

## [0.8.0] - 2019-11-25

### Added

- Added `Analytics.list_data_lake_schemas` to fetch the schemas of each data
  lake table.
- Added `Analytics.get_data_lake_schema` to fetch the schema of a single data
  lake table.
- Added `Analytics.execute_data_lake_query_to_dataframe` to execute a data lake
  query and load the results to a Pandas dataframe.
- Added `Analytics.load_data_lake_result_to_dataframe` to load the results of a
  previously executed data lake query to a Pandas dataframe.
- Added `Files.exists` to check if a file exists.

## [0.7.1] - 2019-11-21

### Fixed

- Fixed issue with `Files.download` to create target directories if they do not
  exist.

## [0.7.0] - 2019-11-20

### Added

- Added optional `pandas` setup install
- Added `ApiResponse.get_as_dataframe` to return a response item as a Pandas
  DataFrame.

## [0.6.0] - 2019-11-01

### Added

- Added the `phc.services.Files` submodule that provides actions for files in
  PHC projects.
- Added the `phc.services.Cohorts` submodule that provides actions for files in
  PHC cohorts.

[0.23.2]: https://github.com/lifeomic/phc-sdk-py/compare/v0.23.1...v0.23.2
[0.23.1]: https://github.com/lifeomic/phc-sdk-py/compare/v0.23.0...v0.23.1
[0.23.0]: https://github.com/lifeomic/phc-sdk-py/compare/v0.22.2...v0.23.0
[0.22.2]: https://github.com/lifeomic/phc-sdk-py/compare/v0.22.1...v0.22.2
[0.22.1]: https://github.com/lifeomic/phc-sdk-py/compare/v0.22.0...v0.22.1
[0.22.0]: https://github.com/lifeomic/phc-sdk-py/compare/v0.21.1...v0.22.0
[0.21.1]: https://github.com/lifeomic/phc-sdk-py/compare/v0.21.0...v0.21.1
[0.21.0]: https://github.com/lifeomic/phc-sdk-py/compare/v0.20.0...v0.21.0
[0.20.0]: https://github.com/lifeomic/phc-sdk-py/compare/v0.19.0...v0.20.0
[0.19.0]: https://github.com/lifeomic/phc-sdk-py/compare/v0.18.1...v0.19.0
[0.18.1]: https://github.com/lifeomic/phc-sdk-py/compare/v0.18.0...v0.18.1
[0.18.0]: https://github.com/lifeomic/phc-sdk-py/compare/v0.17.1...v0.18.0
[0.17.1]: https://github.com/lifeomic/phc-sdk-py/compare/v0.16.0...v0.17.1
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
