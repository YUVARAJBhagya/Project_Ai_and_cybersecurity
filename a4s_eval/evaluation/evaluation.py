
from abc import ABC, abstractmethod
from typing import Protocol, Callable, List

class Model(ABC):
    pass

class Dataset(ABC):
    pass

class Metrics(ABC):
    pass


class DataEvaluator(Protocol):

    def __call__(self, reference: Dataset, evaluated: Dataset) -> List[Metrics]:
        """Run a specific data evaluation.

        Args:
            reference: The reference dataset to run the evaluation.
            evaluated: The evaluaded dataset.

        """
        pass


def data_evaluator() -> Callable[[DataEvaluator], list[Metrics]]:
    """Decorator to register a function as a data evaluator for A4S.


    Returns:
        Callable[[Evaluator], list[Metrics]]: A decorator function that register the evaluation function as data evaluator for A4S
    """

    def func_decorator(func: DataEvaluator) -> list[Metrics]:
        # APPLY LOGIC HERE
        pass

    return func_decorator



@data_evaluator
def drift_evaluator(reference: Dataset, evaluated: Dataset) -> list[Metrics]:

    print("Woooow")
