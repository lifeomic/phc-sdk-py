from enum import Enum


class Zygosity(str, Enum):
    HETEROZYGOUS = "heterozygous"
    HOMOZYGOUS = "homozygous"
    # TODO: Determine if this is a valid option
    REFERENCE_HOMOZYGOUS = "homozygous_reference"
    REFERENCE = "reference"
