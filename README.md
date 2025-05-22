# uber_project

<a target="_blank" href="https://cookiecutter-data-science.drivendata.org/">
    <img src="https://img.shields.io/badge/CCDS-Project%20template-328F97?logo=cookiecutter" />
</a>

Uber assessment for an Automation & Analyst position

## Project Organization

```
├── LICENSE            <- Open-source license if one is chosen
├── Makefile           <- Makefile with convenience commands like `make data` or `make train`
├── README.md          <- The top-level README for developers using this project.
├── data
│   ├── external       <- Data from third party sources.
│   ├── interim        <- Intermediate data that has been transformed.
│   ├── processed      <- The final, canonical data sets for modeling.
│   └── raw            <- The original, immutable data dump.
│
├── docs               <- A default mkdocs project; see www.mkdocs.org for details
│
├── models             <- Trained and serialized models, model predictions, or model summaries
│
├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
│                         the creator's initials, and a short `-` delimited description, e.g.
│                         `1.0-jqp-initial-data-exploration`.
│
├── pyproject.toml     <- Project configuration file with package metadata for 
│                         uber_project and configuration for tools like black
│
├── references         <- Data dictionaries, manuals, and all other explanatory materials.
│
├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
│   └── figures        <- Generated graphics and figures to be used in reporting
│
├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
│                         generated with `pip freeze > requirements.txt`
│
├── setup.cfg          <- Configuration file for flake8
│
└── uber_project       <- Source code for use in this project.
    │
    ├── airflow_dags                
    │   └── weekly_delivery_metrics.py          <- Airflow DAG to calculate main delivery metrics on a weekly basis
    ├── modeling                
    │   ├── models.ipynb                        <- Jupyter notebook that contains the predictive model    
    │   ├── predict.py                          <- Code to run model inference with trained models          
    │   └── train.py                            <- Code to train models
    │
    ├── __init__.py                             <- Makes uber_project a Python module
    │
    ├── dashboard.py                            <- Python script that creates the Streamlit dashboard
    │
    ├── extract.py                              <- Python script that extracts the raw data for analysis, dashboarding and modeling
    │
    ├── features.py                             <- Python script to create features for dashboarding and modeling
    │
    └── transform.py                            <- Python script to transform features for modeling
```

--------

# Uber Assessment 2025 – Python Project Template

This repository contains a clean and reproducible Python 3.8 project setup using:

- `conda` for environment management
- `poetry` for dependency management
- `cookiecutter` for project scaffolding
- `flake8`, `black`, `isort` for code formatting and linting
- `pre-commit` for enforcing code quality before commits

## 🚀 Quick Start

### 1. Clone the repository

```bash


conda create -n uber2025 python=3.9
conda activate uber2025

pip install poetry

poetry install

pre-commit install

# Format code
black .

# Sort imports
isort .

# Run style checks
flake8 .

1. git clone https://github.com/MisaDelgado10/uber_assessment_2025.git
2. cd uber_assessment_2025
3. conda create -n uber_project python=3.9
4. conda activate uber_project
5. pip install poetry
6. pip install pre-commit
7. pre-commit install
8. pip install -r requirements.txt 
9. cd uber_project
10. streamlit run dashboard.py
