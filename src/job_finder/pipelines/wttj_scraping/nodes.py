import html
import logging
import re
import time
from datetime import datetime

import pandas as pd
import requests

from job_finder.utils import generate_payload

logger = logging.getLogger(__name__)


def clean_html_description(raw_html: str) -> str:
    """
    Clean HTML description by removing tags and decoding HTML entities.

    Args:
        raw_html (str): Raw description with HTML

    Returns:
        str: Clean description as plain text
    """
    if not raw_html:
        return ""

    # Decode HTML entities (like &lt; &gt; etc.)
    decoded = html.unescape(raw_html)

    # Remove CDATA if present
    decoded = re.sub(r"<!\[CDATA\[(.*?)\]\]>", r"\1", decoded, flags=re.DOTALL)

    # Remove HTML tags but keep content
    clean_text = re.sub(r"<[^>]+>", "", decoded)

    # Clean multiple spaces and line breaks
    clean_text = re.sub(r"\s+", " ", clean_text).strip()

    return clean_text


def get_job_details(
    session: requests.Session, company_slug: str, job_slug: str
) -> dict:
    """
    Retrieve complete job offer details from WTTJ.

    Args:
        session (requests.Session): HTTP session for requests
        company_slug (str): Company slug
        job_slug (str): Job position slug

    Returns:
        dict: Job offer details including description
    """
    try:
        # API URL to retrieve job offer details
        details_url = f"https://api.welcometothejungle.com/api/v1/organizations/{company_slug}/jobs/{job_slug}"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            "Accept": "application/json",
            "Referer": f"https://www.welcometothejungle.com/fr/companies/{company_slug}/jobs/{job_slug}",
        }

        response = session.get(details_url, headers=headers)

        HTTP_OK = 200
        if response.status_code == HTTP_OK:
            response_data = response.json()
            job_data = response_data.get(
                "job", {}
            )  # The job object is in the "job" key

            # Clean HTML description
            raw_description = job_data.get("description", "")
            clean_description = clean_html_description(raw_description)

            # Clean HTML profile
            raw_profile = job_data.get("profile", "")
            clean_profile = clean_html_description(raw_profile)

            return {
                "description": clean_description,
                "description_raw": raw_description,  # Keep raw version if needed
                "summary": job_data.get("summary", ""),
                "key_missions": job_data.get("key_missions", []),
                "recruitment_process": job_data.get("recruitment_process", ""),
                "company_description": job_data.get("company_description", ""),
                "profile": clean_profile,
                "profile_raw": raw_profile,  # Keep raw version if needed
                "benefits": job_data.get("benefits", {}),
                "skills": job_data.get("skills", []),
                "experience_level": job_data.get("experience_level"),
                "education_level": job_data.get("education_level"),
                "contract_type": job_data.get("contract_type", ""),
                "remote": job_data.get("remote", ""),
                "salary_min": job_data.get("salary_min"),
                "salary_max": job_data.get("salary_max"),
                "salary_currency": job_data.get("salary_currency", ""),
            }
        else:
            logger.warning(
                "Error %s for %s/%s", response.status_code, company_slug, job_slug
            )
            return {}

    except Exception as e:
        logger.error(
            "Error retrieving details for %s/%s: %s", company_slug, job_slug, e
        )
        return {}


def wttj_query_and_parsing(
    headers_jobs: dict, queries: list, number_of_pages_to_search_into: int
) -> pd.DataFrame:
    """
    Query the Welcome to the Jungle (WTTJ) API and parse job offers into a DataFrame.

    Args:
        headers_jobs (dict): HTTP headers used for the API
                            request (e.g., with Algolia credentials).
        queries (list): List of search terms to use in the API requests.
        number_of_pages_to_search_into (int): Number of result pages
                                            to iterate through for each query.

    Returns:
        pd.DataFrame: DataFrame containing parsed job offer
                        data with metadata (company, location,
                        publication date, etc.).
    """
    with requests.Session() as session:
        jobs = []
        for query in queries:
            for page in range(1, number_of_pages_to_search_into + 1):
                data_job_request = generate_payload(query=query, page=page)

                algolia_url = (
                    "https://csekhvms53-dsn.algolia.net/1/indexes/*/queries"
                    "?x-algolia-agent=Algolia%20for%20JavaScript%20(4.20.0)%3B%20Browser"
                    "&search_origin=job_search_client"
                )

                response = session.post(
                    algolia_url, headers=headers_jobs, data=data_job_request
                )
                response_json = response.json()
                for i in range(30):  # Use the same number as function input
                    company_json_tmp = response_json["results"][0]["hits"][i]

                    company_name_tmp = company_json_tmp["organization"].get("name")
                    slug_tmp = company_json_tmp.get("slug")
                    company_slug_tmp = company_json_tmp["organization"].get("slug")

                    # Retrieve complete job offer details
                    job_details = get_job_details(session, company_slug_tmp, slug_tmp)

                    # Small delay to avoid overloading the API
                    time.sleep(0.1)

                    jobs.append(
                        {
                            "reference": company_json_tmp.get("reference"),
                            "company_name": company_name_tmp,
                            "company_slug": company_slug_tmp,
                            "publication_date": company_json_tmp.get(
                                "published_at_date"
                            ),
                            "publication_precise_date": company_json_tmp.get(
                                "published_at"
                            ),
                            "remote": company_json_tmp.get("remote"),
                            "name": company_json_tmp.get("name"),
                            "slug": slug_tmp,
                            "city": company_json_tmp["offices"][0].get("city"),
                            "country": company_json_tmp["offices"][0].get("country"),
                            "education_level": company_json_tmp.get("education_level"),
                            "url": f"https://www.welcometothejungle.com/fr/companies/{company_slug_tmp}/jobs/{slug_tmp}",
                            "logo_url": company_json_tmp["organization"]["logo"].get(
                                "url"
                            ),
                            "description": job_details.get("description", ""),
                            "description_raw": job_details.get("description_raw", ""),
                            "summary": job_details.get("summary", ""),
                            "profile": job_details.get("profile", ""),
                            "profile_raw": job_details.get("profile_raw", ""),
                            "key_missions": job_details.get("key_missions", []),
                            "recruitment_process": job_details.get(
                                "recruitment_process", ""
                            ),
                            "company_description": job_details.get(
                                "company_description", ""
                            ),
                            "benefits": job_details.get("benefits", {}),
                            "skills": ", ".join(
                                [
                                    elt.get("name").get("en")
                                    if isinstance(elt, dict)
                                    and "name" in elt
                                    and "en" in elt["name"]
                                    else None
                                    for elt in job_details.get("skills", [])
                                ]
                            ),
                            "experience_level_detailed": job_details.get(
                                "experience_level"
                            ),
                            "education_level_detailed": job_details.get(
                                "education_level"
                            ),
                            "contract_type_detailed": job_details.get(
                                "contract_type", ""
                            ),
                            "remote_detailed": job_details.get("remote", ""),
                            "salary_min": job_details.get("salary_min"),
                            "salary_max": job_details.get("salary_max"),
                            "salary_currency": job_details.get("salary_currency", ""),
                        }
                    )

        wttj_jobs = pd.DataFrame(jobs)
    return wttj_jobs


# TODO: filter on date and change function name
def jobs_filtering(
    wttj_jobs: pd.DataFrame,
    queries: list,
) -> pd.DataFrame:
    """
    Filter job offers based on whether the job title contains one of the query terms.

    Args:
        wttj_jobs (pd.DataFrame): DataFrame containing job offers.
        queries (list): List of keywords to match in the 'name' (title) of the job offers.

    Returns:
        pd.DataFrame: Filtered DataFrame with unique job offers whose titles match any query term.
    """
    wttj_jobs = wttj_jobs.loc[
        wttj_jobs["name"].str.contains("|".join(queries), case=False)
    ]
    wttj_jobs = wttj_jobs.drop_duplicates(subset="reference")
    return wttj_jobs


# DEPRECATED: S3 functionality disabled in favor of Azure
# def s3_uploading(wttj_jobs: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
#     """
#     Prepare job data for S3 uploading by adding metadata and timestamping the scrape.
#
#     Args:
#         wttj_jobs (pd.DataFrame): DataFrame containing job offers to be uploaded.
#
#     Returns:
#         tuple:
#             - pd.DataFrame: DataFrame with a new 'provider' column added.
#             - dict: Dictionary containing a timestamp under the key 'last_scrape'.
#     """
#     wttj_jobs["provider"] = "Welcome to the jungle"
#
#     now = datetime.now().isoformat()
#     last_scrape = {"last_scrape": now}
#     return wttj_jobs, last_scrape


def save_to_azure_and_chromadb(wttj_jobs: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """
    Save job data to both Azure Blob Storage (Excel) and ChromaDB for vector similarity search.
    Also generates the last scrape timestamp.

    Args:
        wttj_jobs (pd.DataFrame): DataFrame containing job offers.

    Returns:
        tuple:
            - pd.DataFrame: DataFrame with a new 'provider' column added (for Azure).
            - dict: Dictionary containing a timestamp under the key 'last_scrape'.
    """
    # Add provider column for Azure storage
    wttj_jobs_with_provider = wttj_jobs.copy()
    wttj_jobs_with_provider["provider"] = "Welcome to the jungle"

    # Generate timestamp for last scrape
    now = datetime.now().isoformat()
    last_scrape = {"last_scrape": now}

    return wttj_jobs_with_provider, last_scrape


def save_to_chromadb(wttj_jobs: pd.DataFrame):
    """
    Save job data to ChromaDB for vector similarity search.

    Args:
        wttj_jobs (pd.DataFrame): DataFrame containing job offers.

    Returns:
        pd.DataFrame: The input DataFrame (pass-through for pipeline compatibility).
    """
    # Add provider column for ChromaDB
    wttj_jobs_with_provider = wttj_jobs.copy()
    wttj_jobs_with_provider["provider"] = "Welcome to the jungle"

    return wttj_jobs_with_provider
