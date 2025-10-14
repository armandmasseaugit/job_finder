import logging
import smtplib
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import pandas as pd
from job_finder.settings import credentials

logger = logging.getLogger(__name__)


def filter_new_jobs(wttj_jobs: pd.DataFrame) -> list:
    """Filter jobs published in the last 2 days.

    Args:
        wttj_jobs (pd.DataFrame): DataFrame containing all current scraped job offers.

    Returns:
        list: List of recent job offers (published within 2 days), converted to dicts.
    """
    wttj_jobs["publication_date"] = pd.to_datetime(
        wttj_jobs["publication_date"], errors="coerce"
    )
    cutoff_date = datetime.now() - timedelta(days=2)
    recent_jobs = wttj_jobs[wttj_jobs["publication_date"] >= cutoff_date]
    return recent_jobs.to_dict(orient="records")


def send_email(new_jobs: list, config: dict) -> None:
    """Send an email notification if new job offers are found.

    Args:
        new_jobs (list): List of new job offers as dictionaries.
        config (dict): Email configuration with sender and recipient.

    Returns:
        None
    """
    # if not new_jobs:
    #     print("No new job offers to notify.")
    #     return

    subject = f"{len(new_jobs)} new job offer(s) this week 🚀"
    body = "\n\n".join(
        [
            f"{job['name']} at {job['company_name']}\n{job.get('url', 'No URL')}"
            for job in new_jobs
        ]
    )

    message = MIMEMultipart()
    message["From"] = config["email_from"]
    message["To"] = config["email_to"]
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(config["email_from"], credentials.get("sender_email_password"))
        server.sendmail(config["email_from"], config["email_to"], message.as_string())
        logger.info("Sent email with %d new offers.", len(new_jobs))
