from enum import Enum


class CopyNumberStatus(str, Enum):
    AMPLIFICATION = "amplification"
    GAIN = "gain"
    NEUTRAL = "neutral"
    PARTIAL_LOSS = "partialLoss"
    LOSS = "loss"
