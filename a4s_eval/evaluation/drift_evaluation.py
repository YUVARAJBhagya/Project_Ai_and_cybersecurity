from a4s_eval.evaluation.evaluation import DataEvaluation, Dataset

class DriftEvaluation(DataEvaluation):

    def eval(self, reference: Dataset, evaluated: Dataset):
        return super().eval(reference, evaluated)
