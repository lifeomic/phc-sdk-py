from enum import Enum


class CodingEffect(str, Enum):
    FRAMESHIFT = "frameshift"
    SPLICE_REGION = "splice_region"
    SPLICE_SITE = "splice_site"
    STOP_LOST = "stop_lost"
    START_LOST = "start_lost"
    NONSENSE = "nonsense"
    INFRAME = "inframe"
    MISSENSE = "missense"
    UTR3 = "UTR3"
    UTR5 = "UTR5"
    SYNONYMOUS = "synonymous"
