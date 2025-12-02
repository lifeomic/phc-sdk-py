import pandas as pd

from phc.easy.clinical_impression import ClinicalImpression


def test_table_name():
    assert ClinicalImpression.table_name() == "clinical_impression"


def test_code_fields():
    code_fields = ClinicalImpression.code_fields()
    assert "meta.tag" in code_fields
    assert "code.coding" in code_fields


def test_transform_results_with_empty_dataframe():
    df = pd.DataFrame()
    result = ClinicalImpression.transform_results(df)
    assert isinstance(result, pd.DataFrame)


def test_transform_results_with_basic_data():
    df = pd.DataFrame(
        [
            {
                "id": "impression1",
                "status": "completed",
                "summary": "Patient shows improvement",
                "description": "Musculoskeletal",
                "effectiveDateTime": "2023-01-15T10:30:00-05:00",
            },
            {
                "id": "impression2",
                "status": "draft",
                "summary": "Initial assessment",
                "description": "Cardiovascular",
                "effectiveDateTime": "2023-02-20T14:00:00-05:00",
            },
        ]
    )
    result = ClinicalImpression.transform_results(df)
    assert "id" in result.columns
    assert "status" in result.columns
    assert "summary" in result.columns
    assert "description" in result.columns
    assert len(result) == 2

