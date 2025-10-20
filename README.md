# Job Finder

## Turned job hunting into a personalized daily briefing

**Ever spent hours scrolling through job boards, jumping from site to site, only to find the same irrelevant listings—or worse, miss the good ones entirely?**

This project was born out of that exact pain. Job hunting shouldn't be tedious or chaotic.

That's why this end-to-end system automates job offer discovery across platforms and uses user feedback to train a machine learning model that ranks jobs by relevance. It combines data collection via web scraping, model training, and deployment in a streamlined pipeline that delivers daily personalized recommendations via email and an interactive web app.

The screenshot below shows the interface with job offers sorted by relevance,
and the mouse hovering over the "like" button, ready to provide feedback to the model.

<div align="center">
  <img src="https://github.com/user-attachments/assets/c1b122b6-6656-4089-8b0e-8e333a92ee2e"
       alt="Screenshot of the job finder app with job listings sorted by relevance. The mouse is hovering over the 'like' button, ready to provide feedback."
       height="450"/>
</div>


## Technology Stack

- **Python 3.8+**
- **Kedro**: for building reproducible and modular data pipelines.
- **Pandas, NumPy**: data manipulation and processing.
- **scikit-learn**: for machine learning (SGDClassifier, TF-IDF vectorization).
- **FastAPI**: backend API serving job offers, relevance scores, and feedback handling.
- **Streamlit**: web app frontend.
- **AWS S3**: storage of scraped data, models, and results.
- **Email service**: to send daily summaries (SMTP or any email API).
- **Docker**: for containerized deployment.
- **GitHub Actions**: CI/CD for testing, building, and deploying Docker containers.
- **Redis**: in-memory key-value store used for caching and fast data access.
- **Airflow** – Workflow orchestration for scheduling pipelines.
- **Kubernetes** – Scalable deployment and job orchestration.

<div align="center">
  <img src="docs/source/architecture.png" alt="Architecture Diagram" height="600"/>
</div>

## Contributing

Want to contribute to this project? Please read our [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to get started, coding standards, and the development workflow.

## Secrets Management

In a typical Kedro setup, secrets are managed by placing credential files inside the `conf/`
directory, excluding them via `.gitignore`, and injecting them through GitHub Actions using
GitHub Secrets. This allows the secret YAML files to be recreated at build time before pushing
to Docker Hub. This approach is suitable for **private images**, as credentials can safely be embedded
inside the Docker image.

However, since my Docker image is **public**, I avoid embedding any secrets directly in the image.
Instead, I prefer using **environment variables** to handle credentials securely, depending on the
environment (e.g., local, Kubernetes, or CI/CD pipelines).

## Credits

- Streamlit app sidebar was taken from https://medium.com/@ericdennis7/5-components-that-beautify-your-streamlit-app-79039f405ae1
