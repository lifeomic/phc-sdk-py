from enum import Enum


class GenomicTestType(str, Enum):
    SHORT_VARIANT = "shortVariant"
    EXPRESSION = "expression"
    STRUCTURAL_VARIANT = "structuralVariant"
    COPY_NUMBER_VARIANT = "copyNumberVariant"
    READ = "read"


class GenomicTestStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INDEXING = "INDEXING"
    FAILED = "FAILED"
