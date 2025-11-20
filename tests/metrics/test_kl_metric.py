# importing the necessary libararies
import pandas as pd
import seaborn as sns
from a4s_eval.metrics.data_metrics.kl_metric import compute_kl_for_column


#load the titanic datasets
def load_titanic():
    try:
        return pd.read_csv("data/titanic.csv")
    except:
        return sns.load_dataset("titanic")
    
# Test KL divergence on the first available Titanic column and store the value
def test_kl_is_non_negative():
    df = load_titanic()
    for col in ["class", "pclass", "Pclass", "sex", "embarked"]:
        if col in df.columns:
            target = col
            break

    kl_value = compute_kl_for_column(df, target)

    # check KL value is a non-negative number and valid float
    assert isinstance(kl_value, float)
    assert kl_value >= 0



