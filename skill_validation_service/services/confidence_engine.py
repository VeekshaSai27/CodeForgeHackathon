import numpy as np


def calculate_confidence(correctness):
    if not correctness:
        return 0.5

    variance = np.var(correctness)
    avg = sum(correctness) / len(correctness)

    confidence = avg * (1 - variance)

    return round(confidence, 2)