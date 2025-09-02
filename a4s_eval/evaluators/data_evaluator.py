from typing import Callable, Iterator, Protocol

from a4s_eval.data_model.evaluation import Dataset, DataShape
from a4s_eval.data_model.metric import Metric


class DataEvaluator(Protocol):
    def __call__(
        self, datashape: DataShape, reference: Dataset, evaluated: Dataset
    ) -> list[Metric]:
        """Run a specific data evaluation.

        Args:
            datashape: The datashape of the proejct
            reference: The reference dataset to run the evaluation.
            evaluated: The evaluated dataset.

        """
        raise NotImplementedError


class DataEvaluatorRegistry:
    def __init__(self):
        self._functions = {}

    def register(self, name: str, func: DataEvaluator):
        self._functions[name] = func

    def __iter__(self) -> Iterator[tuple[str, DataEvaluator]]:
        return iter(self._functions.items())


data_evaluator_registry = DataEvaluatorRegistry()


def data_evaluator(name: str) -> Callable[[DataEvaluator], DataEvaluator]:
    """Decorator to register a function as a data evaluator for A4S.
        name: The name to register the evaluator under.

    Returns:
        Callable[[DataEvaluator], DataEvaluator]: A decorator function that registers the evaluation function as a data evaluator for A4S.
    """

    def func_decorator(func: DataEvaluator) -> DataEvaluator:
        data_evaluator_registry.register(name, func)
        return func

    return func_decorator
