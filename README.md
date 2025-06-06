# Job Finder — Automated Job Search and Ranking

## Project Overview

The goal of this project is to automatically search for new job postings that match specific keywords 
(such as "data", "AI", etc.) across multiple websites. Each day, the system emails me summarizing 
the latest relevant job offers. These job listings are also displayed on a Streamlit web app.

On the web app, users can browse the latest offers and provide feedback by liking or disliking each job. 
This feedback is used to train a reinforcement learning model that ranks future offers by relevance. 
Users can then sort the listings based on these relevance scores to see the most personalized opportunities first.


## Features

- Automated web scraping of multiple job platforms for targeted keywords.
- Daily email notifications with summarized relevant job offers.
- Interactive Streamlit app for browsing, liking, and disliking job offers.
- Reinforcement learning model that learns user preferences to rank offers.
- Storage and versioning of data and models on AWS S3.

## Technology Stack

- **Python 3.8+**
- **Kedro**: for building reproducible and modular data pipelines.
- **Pandas, NumPy**: data manipulation and processing.
- **scikit-learn**: for machine learning (SGDClassifier, TF-IDF vectorization).
- **Streamlit**: web app frontend.
- **AWS S3**: storage of scraped data, models, and results.
- **Email service**: to send daily summaries (SMTP or any email API).
- **Optional**: Docker for containerized deployment.


credit: Streamlit app sidebar was taken from https://medium.com/@ericdennis7/5-components-that-beautify-your-streamlit-app-79039f405ae1


Take a look at the [Kedro documentation](https://docs.kedro.org) to get started.

## Rules and guidelines

* Don't commit data to your repository
* Don't commit any credentials or your local configuration to your repository. Keep all your credentials and local configuration in `conf/local/`

## How to install dependencies

To install them, run:

```
make user_install
```

## How to run your Kedro pipeline

You can run your Kedro project with:

```
make run
```

## How to test your Kedro project

Have a look at the files `src/tests/test_run.py` and `src/tests/pipelines/data_science/test_pipeline.py` for instructions on how to write your tests. Run the tests as follows:

```
make test
```

To configure the coverage threshold, look at the `.coveragerc` file.

## Project dependencies

To see and update the dependency requirements for your project use `pyproject.toml`.

[Further information about project dependencies](https://docs.kedro.org/en/stable/kedro_project_setup/dependencies.html#project-specific-dependencies)


