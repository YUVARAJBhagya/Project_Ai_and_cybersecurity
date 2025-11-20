#importing the necessary libraries
import os
import numpy as np
import pandas as pd
from scipy.stats import entropy

# Create a folder named "results", if it does not already exist
os.makedirs("results", exist_ok=True)


def _to_probs(counts, eps=1e-10):
    # Turn counts into probabilities safely, even if all counts are zero
    arr = np.array(counts, dtype=float) + eps
    s = arr.sum()
    if s == 0:
        
        # If all counts were zero, return equal probabilities,otherwise, normalize counts to sum to 1
        return np.ones_like(arr) / len(arr)
    return arr / s


def kl_numeric(ref_col, cur_col, bins=30):
    # Clean numeric data, create histograms for reference and current columns

    r = ref_col.dropna().astype(float)
    c = cur_col.dropna().astype(float)
    if len(r) == 0 or len(c) == 0:
        return float("nan") # Return nan ,if the result cannot be calculated
    
# Create histograms for reference and current data using the same bins to count values in each bin
    counts_r, bin_edges = np.histogram(r, bins=bins)
    counts_c, _ = np.histogram(c, bins=bin_edges)

    p = _to_probs(counts_r)
    q = _to_probs(counts_c)


#This block tries to KL divergence,if anything goes wrong, it safely report the error and return Nan
    try:
        return float(entropy(p, q))
    except Exception as e:
        print(f"[kl_numeric] error: {e}")
        return float("nan")


def kl_categorical(ref_col, cur_col):
    
    # Clean categorical data, count how often each category appears, match categories in both sets
    r = ref_col.dropna().astype(str)
    c = cur_col.dropna().astype(str)

    if len(r) == 0 or len(c) == 0:
        return float("nan")

    p_counts = r.value_counts(normalize=True)
    q_counts = c.value_counts(normalize=True)

    all_vals = p_counts.index.union(q_counts.index)
    p = p_counts.reindex(all_vals, fill_value=0).values
    q = q_counts.reindex(all_vals, fill_value=0).values

    p = _to_probs(p)
    q = _to_probs(q)
    
    #This block tries to KL divergence,if anything goes wrong, it safely report the error and return Nan
    try:
        return float(entropy(p, q))
    except Exception as e:
        print(f"[kl_categorical] error: {e}")
        return float("nan")



def compute_kl_df(ref_df, cur_df, bins=30):
   # Compute KL divergence for each column and store the results in a list
    rows = [] # creating an empty list
    
    #check the column type(numeric or categorical), compute the KLdivergence using appropriate function
    for col in ref_df.columns:
        try:
            if pd.api.types.is_numeric_dtype(ref_df[col]):
                kl_val = kl_numeric(ref_df[col], cur_df[col], bins=bins)
                col_type = "numeric"
            else:
                kl_val = kl_categorical(ref_df[col], cur_df[col])
                col_type = "categorical"
                
                #If the KL calculation fail,print error and mark it as Nan
        except Exception as e:
            print(f"[compute_kl_df] failed for {col}: {e}")
            kl_val = float("nan")
            col_type = "error"
            
# Save each column's KL result in a DataFrame and sort by KL value from highest to lowest
        rows.append({"column": col, "type": col_type, "kl_ref_to_cur": kl_val})

    df = pd.DataFrame(rows)
    return df.sort_values("kl_ref_to_cur", ascending=False).reset_index(drop=True)


def save_kl_results(ref_df, cur_df, out_path="results/titanic_kl_results.csv", bins=30):
    #compute the KL divergence, save the result to csv file and return the dataframe
    df = compute_kl_df(ref_df, cur_df, bins=bins)
    df.to_csv(out_path, index=False)
    print(f"[kl_metric] KL results saved to {out_path}")
    return df


def compute_kl_for_column(a, b, bins=30):
   
    #Compute KL divergence for two Series, return NaN if an error occurs

    if isinstance(a, pd.Series) and isinstance(b, pd.Series):
        try:
            if pd.api.types.is_numeric_dtype(a):
                return kl_numeric(a, b, bins=bins)
            else:
                return kl_categorical(a, b)
        except Exception as e:
            print(f"[compute_kl_for_column] error (series): {e}")
            return float("nan")

    # check if the given column exist in dataframe , return nan if it not exists
    if isinstance(a, pd.DataFrame) and isinstance(b, str):
        df = a
        col = b
        if col not in df.columns:
            print(f"[compute_kl_for_column] error: column '{col}' not in DataFrame")
            return float("nan")
        
        
        # Split the column into two parts and calculate KL divergence, return nan if something goes wrong
        try:
            ref = df.sample(frac=0.7, random_state=1).reset_index(drop=True)
            cur = df.drop(ref.index).reset_index(drop=True)
            ref_series = ref[col]
            cur_series = cur[col]
            if pd.api.types.is_numeric_dtype(ref_series):
                return kl_numeric(ref_series, cur_series, bins=bins)
            else:
                return kl_categorical(ref_series, cur_series)
        except Exception as e:
            print(f"[compute_kl_for_column] error (df split): {e}")
            return float("nan")

    # handling the invalid input type by printing a message and return nan
    print("[compute_kl_for_column] unsupported input types")
    return float("nan")
