#importing necessary libararies
import seaborn as sns
import pandas as pd
import os

def main():
    os.makedirs("data", exist_ok=True)# creating the data folder, if it doesn't exist
    #load the titanic dataset
    print("Loading Titanic dataset")
    df = sns.load_dataset("titanic")

    # Sort the dataset by age and reset the row index
    df = df.sort_values("age").reset_index(drop=True)

    
    p1 = df.iloc[:400]   # old data
    p2 = df.iloc[400:]   # new data

    # introducing a small drift by increasing all age value in p2 by 3
    if "age" in p2.columns:
        p2["age"] = p2["age"] + 3

    p1.to_csv("data/titanic_period1.csv", index=False)
    p2.to_csv("data/titanic_period2.csv", index=False)

    print("Created:")
    print(" data/titanic_period1.csv")
    print(" data/titanic_period2.csv")
    
# Start the program by calling main() when running this file
if __name__ == "__main__":
    main()


