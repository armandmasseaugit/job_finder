import json
import urllib.parse


def generate_payload(query, page=0, hits_per_page=30):
    """
    Generate a payload for querying the Welcome to the Jungle job API via Algolia.

    Args:
        query (str): Search query string to filter job titles.
        page (int, optional): Page number to fetch (0-indexed). Defaults to 0.
        hits_per_page (int, optional): Number of results per page. Defaults to 30.

    Returns:
        str: JSON-formatted string representing the Algolia payload for the job search query.

    Note:
        - The function constructs the payload using various filters and display options, such as excluding certain fields,
          limiting facets, and applying search analytics tags.
        - The payload can be used with a POST request to the Algolia API endpoint.
    """

    attributes_to_retrieve = [
        "*",
        "-has_benefits",
        "-has_contract_duration",
        "-has_education_level",
        "-has_experience_level_minimum",
        "-has_remote",
        "-has_salary_yearly_minimum",
        "-new_profession",
        "-organization.description",
        "-organization_score",
        "-profile",
        "-rank_group_1",
        "-rank_group_2",
        "-rank_group_3",
        "-sectors",
        "-source_stage",
        "description",
        "content",
        "details",
        "summary",
    ]

    response_fields = [
        "facets",
        "hits",
        "hitsPerPage",
        "nbHits",
        "nbPages",
        "page",
        "params",
        "query",
    ]

    analytics_tags = ["page:jobs_index", "language:fr"]

    facets = [
        "_collections",
        "benefits",
        "organization.commitments",
        "contract_type",
        "contract_duration_minimum",
        "contract_duration_maximum",
        "has_contract_duration",
        "education_level",
        "has_education_level",
        "experience_level_minimum",
        "has_experience_level_minimum",
        "organization.nb_employees",
        "organization.labels",
        "salary_yearly_minimum",
        "has_salary_yearly_minimum",
        "salary_currency",
        "followedCompanies",
        "language",
        "new_profession.category_reference",
        "new_profession.sub_category_reference",
        "remote",
        "sectors.parent_reference",
        "sectors.reference",
    ]

    encoded_params = urllib.parse.urlencode(
        {
            "attributesToHighlight": json.dumps(["name"]),
            "attributesToRetrieve": json.dumps(attributes_to_retrieve),
            "clickAnalytics": "true",
            "hitsPerPage": hits_per_page,
            "maxValuesPerFacet": 999,
            "responseFields": json.dumps(response_fields),
            "analytics": "true",
            "enableABTest": "true",
            "userToken": "8f6e8ea0-510c-4e3d-b888-70734beab944",
            "analyticsTags": json.dumps(analytics_tags),
            "facets": json.dumps(facets),
            "filters": '("offices.country_code":"FR") AND ("contract_type": "full_time")',
            "page": page,
            "query": query,
        },
        quote_via=urllib.parse.quote,
    )

    payload = {
        "requests": [
            {
                "indexName": "wttj_jobs_production_fr_published_at_desc",
                "params": encoded_params,
            }
        ]
    }

    return json.dumps(payload, indent=2)
