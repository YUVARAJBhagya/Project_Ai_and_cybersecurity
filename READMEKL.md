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




when you unzip the file then do uv sync

when u do pip install seaborn if u get anything like this

pip install seaborn
error: externally-managed-environment

× This environment is externally managed
╰─> To install Python packages system-wide, try apt install
    python3-xyz, where xyz is the package you are trying to
    install.
    
    If you wish to install a non-Debian-packaged Python package,
    create a virtual environment using python3 -m venv path/to/venv.
    Then use path/to/venv/bin/python and path/to/venv/bin/pip. Make
    sure you have python3-full installed.
    
    If you wish to install a non-Debian packaged Python application,
    it may be easiest to use pipx install xyz, which will manage a
    virtual environment for you. Make sure you have pipx installed.
    
    See /usr/share/doc/python3.12/README.venv for more information.

note: If you believe this is a mistake, please contact your Python installation or OS distribution provider. You can override this, at the risk of breaking your Python installation or OS, by passing --break-system-packages.
hint: See PEP 668 for the detailed specification

please do this steps it will work
cd /home/bhagya/Project_Ai_and_cybersecurity
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install seaborn pytest
