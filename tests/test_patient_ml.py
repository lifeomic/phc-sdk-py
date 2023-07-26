import os
from unittest.mock import MagicMock, patch

from phc.util.patient_ml import retrieve_label_defs
from phc.services.patient_ml import LabelsDefinition


def test_retrieve_label_defs_during_training_stage():
    mock_parse_file = MagicMock(return_value={})

    with patch.object(LabelsDefinition, "parse_file", mock_parse_file):
        retrieve_label_defs()

    mock_parse_file.assert_called_once_with(
        "/opt/ml/input/data/metadata/labels.json"
    )


def test_retrieve_label_defs_during_custom_evaluation_stage(monkeypatch):
    # simulate the use case of evaluation stage
    mock_metadata_dir = "tests/patient_ml/input/data/metadata"
    monkeypatch.setenv("METADATA_DIR", mock_metadata_dir)

    mock_parse_file = MagicMock(return_value={})

    with patch.object(LabelsDefinition, "parse_file", mock_parse_file):
        retrieve_label_defs()

    mock_parse_file.assert_called_once_with(f"{mock_metadata_dir}/labels.json")
