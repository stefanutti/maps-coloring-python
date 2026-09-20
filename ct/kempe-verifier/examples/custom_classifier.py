"""Demonstration only: demand the good sector E0, leave other good sectors unknown."""

from kempe.model import Classification, r5


def classify(state):
    verdict = r5(state)
    if verdict.kind == 'good' and verdict.sector != 'E0':
        return Classification('unknown', 'Example target accepts only fan 0; this is not the R5 criterion')
    return verdict
