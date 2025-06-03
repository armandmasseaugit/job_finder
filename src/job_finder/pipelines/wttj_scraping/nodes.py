from job_finder.utils import generate_payload
import pandas as pd
import requests
from datetime import datetime


def wttj_query_and_parsing(
    headers_jobs: dict, queries: list, number_of_pages_to_search_into: int
) -> pd.DataFrame:
    with requests.Session() as session:
        jobs = []
        for query in queries:
            for page in range(1, number_of_pages_to_search_into + 1):

                data_job_request = generate_payload(query=query, page=page)

                response = session.post(
                    "https://csekhvms53-dsn.algolia.net/1/indexes/*/queries?x-algolia-agent=Algolia%20for%20JavaScript%20(4.20.0)%3B%20Browser&search_origin=job_search_client",
                    headers=headers_jobs,
                    data=data_job_request,
                )
                response_json = response.json()
                for i in range(30):  # Mettre le meme nb que en entree de la fonction
                    company_json_tmp = response_json["results"][0]["hits"][i]
                    # Note: pour le moment, on se contente juste de  chercher parmi le titre des offres. on donne l'url mais
                    # il faudrait aller sur cet url pour afficher details de l'offre.
                    #
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


# TODO: filter on date
def jobs_filtering(wttj_jobs: pd.DataFrame, queries: list) -> pd.DataFrame:
    wttj_jobs = wttj_jobs.loc[
        wttj_jobs["name"].str.contains("|".join(queries), case=False)
    ]
    return wttj_jobs


def s3_uploading(wttj_jobs: pd.DataFrame) -> [pd.DataFrame, dict]:
    now = datetime.now().isoformat()
    last_scrape = {"last_scrape": now}
    return wttj_jobs, last_scrape
