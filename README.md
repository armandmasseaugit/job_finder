# Job Finder

## Turned job hunting into a personalized daily briefing

End-to-end system that automates job offer discovery across platforms and uses user feedback to train a machine learning model ranking jobs by relevance. 
The system combines data collection via web scraping, model training, and deployment in a streamlined pipeline that delivers daily personalized recommendations via email and an interactive web app.

The screenshot below shows the interface with job offers sorted by relevance, 
and the mouse hovering over the "like" button, ready to provide feedback to the model.

![Screenshot of the job finder app with job listings sorted by relevance. The mouse is hovering over the 'like' button, ready to provide feedback.](https://github.com/user-attachments/assets/c1b122b6-6656-4089-8b0e-8e333a92ee2e)


## Technology Stack

- **Python 3.8+**
- **Kedro**: for building reproducible and modular data pipelines.
- **Pandas, NumPy**: data manipulation and processing.
- **scikit-learn**: for machine learning (SGDClassifier, TF-IDF vectorization).
- **Streamlit**: web app frontend.
- **AWS S3**: storage of scraped data, models, and results.
- **Email service**: to send daily summaries (SMTP or any email API).
- **Docker**: for containerized deployment.
- **Airflow** (coming soon) – Workflow orchestration for scheduling pipelines.
- **Kubernetes** (coming soon) – Scalable deployment and job orchestration.

<img src="docs/source/architecture.png" alt="Architecture Diagram" height="400"/>

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


## Git Workflow & Naming Conventions

To ensure clarity and consistency in version control, this project follows a set of conventional branch and commit naming standards inspired by common Git practices.

### Branch Types

| Type      | Purpose                                                                 |
|-----------|-------------------------------------------------------------------------|
| fix       | For fixing non-critical bugs during development                         |
| hotfix    | For urgent bug fixes made directly on the `main` branch                 |
| feature   | For developing new features                                             |
| release   | For preparing code for production (e.g., version bump, final tests)     |
| chore     | For routine tasks like updating documentation or dependencies           |
| refactor  | For restructuring code without changing its behavior or functionality   |

Branch names typically follow this format:

```
<type>/<short-description>
```

Example: `feature/job-scoring`, `fix/missing-logo-url`

### Commit Types


| Prefix     | Use Case                                                       |
|------------|----------------------------------------------------------------|
| feat       | For introducing a new feature                                  |
| fix        | For fixing a bug                                               |
| docs       | For documentation changes only                                 |
| style      | For code formatting, white-space, etc. (no code behavior change)|
| refactor   | For code changes that neither fix bugs nor add features        |
| perf       | For performance improvements                                   |
| test       | For adding or updating tests                                   |
| ci         | For changes to CI/CD configuration files and scripts           |
| chore      | For minor tasks like dependency updates or file renaming       |

Commit message format:

```
<type>: short description of the change
```

Example:

```
feat: add job relevance scoring model
fix: correct scraping URL construction
chore: update requirements.txt
```

This structure makes it easier to automate release notes, understand project history, and onboard contributors.


