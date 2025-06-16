
from a4s_eval.evaluations.data_evaluation.registry import Dataset, Metrics, data_evaluator

@data_evaluator()
def empty_data_evaluator(reference: Dataset, evaluated: Dataset) -> list[Metrics]:
    return []
