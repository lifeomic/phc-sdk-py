from enum import Enum


class Zygosity(str, Enum):
    HETEROZYGOUS = "heterozygous"
    HOMOZYGOUS = "homozygous"
    REFERENCE = "reference"
