import pandas as pd
from a4s_eval.metrics.data_metrics.kl_metric import compute_kl_df, save_kl_results

def main():
    
    #load the titanic dataset
    p1 = pd.read_csv("data/titanic_period1.csv")
    p2 = pd.read_csv("data/titanic_period2.csv")
    
   #compute the KL divergence to measure how much data has changed
    print("Computing KL divergence")
    df = save_kl_results(p1, p2, "results/titanic_kl_results.csv")
    print(df.head())
  
    
#start the program by calling the main()
if __name__ == "__main__":
    main()