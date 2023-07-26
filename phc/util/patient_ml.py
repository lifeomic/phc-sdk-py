import os
from phc.services.patient_ml import LabelsDefinition

# be able to override base directory for testing
_base_dir = os.environ.get("PATIENT_ML_BASE_PATH", "/opt/ml")
_channel_input_dirs = {
    channel_name: os.path.join(_base_dir, "input", "data", channel_name)
    for channel_name in ["train", "val", "metadata"]
}


def retrieve_label_defs() -> LabelsDefinition:
    """Returns a LabelsDefinition object from training/evaluation stage."""
    return LabelsDefinition.parse_file(
        os.path.join(
            os.environ.get("METADATA_DIR", _channel_input_dirs["metadata"]),
            "labels.json",
        )
    )
