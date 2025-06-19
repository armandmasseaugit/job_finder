from datetime import datetime
import requests
from job_finder.utils import generate_payload
import pandas as pd


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
                for i in range(30):  # Mettre le meme nb que en entree de la fonction
                    company_json_tmp = response_json["results"][0]["hits"][i]
                    # TODO: search offer details

                    company_name_tmp = company_json_tmp["organization"].get("name")
                    slug_tmp = company_json_tmp.get("slug")
                    company_slug_tmp = company_json_tmp["organization"].get("slug")

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
                        }
                    )

        wttj_jobs = pd.DataFrame(jobs)
    return wttj_jobs


# TODO: filter on date et chnager de nom de fonction
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


def s3_uploading(wttj_jobs: pd.DataFrame) -> [pd.DataFrame, dict]:
    """
    Prepare job data for S3 uploading by adding metadata and timestamping the scrape.

    Args:
        wttj_jobs (pd.DataFrame): DataFrame containing job offers to be uploaded.

    Returns:
        tuple:
            - pd.DataFrame: DataFrame with a new 'provider' column added.
            - dict: Dictionary containing a timestamp under the key 'last_scrape'.
    """
    wttj_jobs["provider"] = "Welcome to the jungle"

    now = datetime.now().isoformat()
    last_scrape = {"last_scrape": now}
    return wttj_jobs, last_scrape
