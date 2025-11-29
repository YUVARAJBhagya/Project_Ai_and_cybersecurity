Kullback–Leibler (KL) Divergence. 
URL of github: https://github.com/YUVARAJBhagya/Project_Ai_and_cybersecurity.git

First need to install evidently:pip install evidently(version 0.7.16) 
pip install seaborn to import (load the dataset)

I implemented the metrics in file kl_metric.py(to run :python -m a4s_eval.metrics.data_metrics.kl_metric )

A test file named test_kl_metric.py was added to verify the KL divergence function.
TO run the test file:uv run pytest tests/metrics/data_metrics/test_kl_metric.py 

Scripts: The project contains three main scripts 
it contain 3 files
1.generate_titanic_datasets.py:Creates the Titanic datasets, simulating drift by modifying the 
age feature.(To run this:python scripts/generate_titanic_datasets.py )
2.run_evidently_report.py:Runs the Evidently dashboard, generating the visual report(To run this:python scripts/run_evidently_report.py )
3.run_kl.py:Computes KL divergence and outputs the results. (python scripts/run_kl.py)

Output is stored in titanic_drift_report.html(to open this right click select reveal in file explorer)

