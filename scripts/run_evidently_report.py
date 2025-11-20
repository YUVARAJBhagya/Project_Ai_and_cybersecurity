#importing necessary libarires
import os
import math
import pandas as pd
import matplotlib.pyplot as plt

#  Import function to calculate KL divergence for all columns in two datasets
from a4s_eval.metrics.data_metrics.kl_metric import compute_kl_df

def safe_series(series):
   #This function removes missing values  from a column so calculations can be done safely
    return series.dropna()

def make_numeric_plot(ref, cur, column, out_file):
    #clean the numeric data from missing values so we can safetly plot it
    r = safe_series(ref[column])
    c = safe_series(cur[column])

    # convert to float for plotting if possible, if it fail's use the original value
    try:
        r_vals = r.astype(float)
    except Exception:
        r_vals = r

    try:
        c_vals = c.astype(float)
    except Exception:
        c_vals = c

    plt.figure(figsize=(6, 4))# Create a new plot figure with width 6 inches and height 4 inches

    # plot the histogram if the data is not empty
    if len(r_vals) > 0:
        plt.hist(r_vals, bins=25, alpha=0.6, label="Reference")
    if len(c_vals) > 0:
        plt.hist(c_vals, bins=25, alpha=0.6, label="Current")

    plt.title(f"{column} (numeric)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_file)
    plt.close()
    
    

def make_categorical_plot(ref, cur, column, out_file):
    # clean the categorical data from missing values so we can safetly plot it
    r = safe_series(ref[column]).astype(str)
    c = safe_series(cur[column]).astype(str)

# Get category counts from both columns and build a combined list of all categories
    r_counts = r.value_counts()
    c_counts = c.value_counts()
    cats = sorted(set(r_counts.index).union(set(c_counts.index)))
    
    
# Get counts for each category in both datasets and set positions for the bar chart
    r_vals = [r_counts.get(cat, 0) for cat in cats]
    c_vals = [c_counts.get(cat, 0) for cat in cats]
    x = range(len(cats))
    width = 0.35
    plt.figure(figsize=(6, 4))
    plt.bar([i - width/2 for i in x], r_vals, width=width, label="Reference", alpha=0.6)
    plt.bar([i + width/2 for i in x], c_vals, width=width, label="Current", alpha=0.6)
    plt.xticks(x, cats, rotation=45, ha="right", fontsize=8)
    plt.title(f"{column} (categorical)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_file)
    plt.close()



def main():
    # checks folders exist
    os.makedirs("reports/plots", exist_ok=True)
    os.makedirs("reports", exist_ok=True)

#set the file path for reference and current titanic dataset
    ref_path = "data/titanic_period1.csv"
    cur_path = "data/titanic_period2.csv"

#check if the reference or current csv if exists otherwise raise an error
    if not os.path.exists(ref_path) or not os.path.exists(cur_path):
        raise FileNotFoundError("Please create data/titanic_period1.csv and data/titanic_period2.csv first.")
    print("Loading Titanic datasets")
    ref = pd.read_csv(ref_path)
    cur = pd.read_csv(cur_path)
    print("Reference rows:", len(ref), "Current rows:", len(cur))

    
    #compute KL divergence, save the result in csv file
    print("Computing KL divergence per column")
    kl_table = compute_kl_df(ref, cur)
    csv_path = "reports/titanic_kl_summary.csv"
    kl_table.to_csv(csv_path, index=False)
    print("Saved KL summary to:", csv_path)

    # Generate plots for each column
    print("Generating plots")
    plot_paths = {}
    for column in ref.columns:
        # create safe filename
        safe_name = column.replace(" ", "_").replace("/", "_")
        out_file = f"reports/plots/{safe_name}.png"

        # check whether the column is numeric, or categorical
        if pd.api.types.is_bool_dtype(ref[column]) or pd.api.types.is_object_dtype(ref[column]) or pd.api.types.is_categorical_dtype(ref[column]):
            
            #try to create a categorical plot for the column, if it is fail print the warning message
            try:
                make_categorical_plot(ref, cur, column, out_file)
            except Exception as e:
                print(f"Warning: failed to plot categorical column {column}: {e}")
                
                
                # create an empty placeholder image so HTML still loads
                plt.figure(figsize=(4,2)); plt.text(0.5,0.5,"No plot",ha='center'); plt.axis('off'); plt.savefig(out_file); plt.close()
                
                
                #Safely plot numeric columns
        elif pd.api.types.is_numeric_dtype(ref[column]):
           
            try:
                make_numeric_plot(ref, cur, column, out_file)
            except Exception as e:
                print(f"Warning: failed to plot numeric column {column}: {e}")
                plt.figure(figsize=(4,2)); plt.text(0.5,0.5,"No plot",ha='center'); plt.axis('off'); plt.savefig(out_file); plt.close()
        else:
            # fallback treat it as categorical ,try to plot it
            try:
                make_categorical_plot(ref, cur, column, out_file)
            except Exception as e:
                print(f"Warning: failed to plot column {column}: {e}")
                plt.figure(figsize=(4,2)); plt.text(0.5,0.5,"No plot",ha='center'); plt.axis('off'); plt.savefig(out_file); plt.close()

        plot_paths[column] = out_file
        
        

    # Create a  HTML report that shows the KL table and column plot
    print("Creating HTML report.")
    html_path = "reports/titanic_drift_report.html"
    with open(html_path, "w", encoding="utf-8") as f:
        f.write("<html><head><meta charset='utf-8'><title>Titanic Drift Report</title></head><body>\n")
        f.write("<h1>Titanic Drift Report</h1>\n")
        f.write(f"<p>Reference: {ref_path} ({len(ref)} rows) — Current: {cur_path} ({len(cur)} rows)</p>\n")
        f.write("<h2>KL Divergence Summary</h2>\n")
        f.write(kl_table.to_html(index=False))
        f.write("<h2>Column Plots</h2>\n")
        for col in ref.columns:
            f.write(f"<h3>{col}</h3>\n")
            f.write(f"<img src='plots/{col.replace(' ', '_').replace('/', '_')}.png' style='max-width:900px;'><br>\n")
        f.write("</body></html>")

    print("Saved HTML report to:", html_path)
    print("Open the HTML report in your browser")

if __name__ == "__main__":
    main()



