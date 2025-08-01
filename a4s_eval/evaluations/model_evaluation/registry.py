from typing import Callable, Iterator, List, Protocol

from a4s_eval.data_model.evaluation import Dataset, Model
from a4s_eval.data_model.metric import Metric


class ModelEvaluator(Protocol):
    def __call__(self, reference: Model, evaluate: Dataset) -> List[Metric]:
        """Run a specific model evaluation.

        Args:
            reference: The reference model to run the evaluation.
            evaluate: The evaluated dataset.

        """
        pass


class ModelEvaluatorRegistry:
    def __init__(self):
        self._functions = {}

    def register(self, name: str, func: ModelEvaluator):
        self._functions[name] = func

    def __iter__(self) -> Iterator[tuple[str, ModelEvaluator]]:
        return iter(self._functions.items())


model_evaluator_registry = ModelEvaluatorRegistry()


def model_evaluator(name: str) -> Callable[[ModelEvaluator], list[Metric]]:
    """Decorator to register a function as a model evaluator for A4S.

    Args:INSERT INTO model (id, pid, name, data, project_id, dataset_id)
    VALUES (
        id:integer,
        'pid:uuid',
        'name:character varying',
        'data:character varying',
        project_id:integer,
        dataset_id:integer
      );
        name: The name to register the evaluator under.

    Returns:
        Callable[[Evaluator], list[Metrics]]: A decorator function that registers the evaluation function as a data evaluator for A4S.
    """

    def func_decorator(func: ModelEvaluator) -> None:
        model_evaluator_registry.register(name, func)
        return func

    return func_decorator
