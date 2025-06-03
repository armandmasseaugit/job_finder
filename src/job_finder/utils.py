import urllib
import json


def generate_payload(query, page=0, hits_per_page=30):
    encoded_params = urllib.parse.urlencode(
        {
            "attributesToHighlight": '["name"]',
            "attributesToRetrieve": '["*", "-has_benefits", "-has_contract_duration", "-has_education_level", "-has_experience_level_minimum", "-has_remote", "-has_salary_yearly_minimum", "-new_profession", "-organization.description", "-organization_score", "-profile", "-rank_group_1", "-rank_group_2", "-rank_group_3", "-sectors", "-source_stage"]',
            "clickAnalytics": "true",
            "hitsPerPage": hits_per_page,
            "maxValuesPerFacet": 999,
            "responseFields": '["facets", "hits", "hitsPerPage", "nbHits", "nbPages", "page", "params", "query"]',
            "analytics": "true",
            "enableABTest": "true",
            "userToken": "8f6e8ea0-510c-4e3d-b888-70734beab944",
            "analyticsTags": '["page:jobs_index", "language:fr"]',
            "facets": '["_collections", "benefits", "organization.commitments", "contract_type", "contract_duration_minimum", "contract_duration_maximum", "has_contract_duration", "education_level", "has_education_level", "experience_level_minimum", "has_experience_level_minimum", "organization.nb_employees", "organization.labels", "salary_yearly_minimum", "has_salary_yearly_minimum", "salary_currency", "followedCompanies", "language", "new_profession.category_reference", "new_profession.sub_category_reference", "remote", "sectors.parent_reference", "sectors.reference"]',
            "filters": '("offices.country_code":"FR") AND ("contract_type": "full_time")',  # C'est ici que sont gérés les filtres
            "page": page,
            "query": query,
        },
        quote_via=urllib.parse.quote,
    )

    payload = {
        "requests": [
            {
                "indexName": "wttj_jobs_production_fr_published_at_desc",  # enlever published_at_desc pour elever le filtre de tri par date
                "params": encoded_params,
            }
        ]
    }

    return json.dumps(payload, indent=2)
