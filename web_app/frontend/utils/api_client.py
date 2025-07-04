import requests

API_BASE = "http://localhost:8000"

def get_offers():
    return requests.get(f"{API_BASE}/offers").json()

def get_likes():
    return requests.get(f"{API_BASE}/likes").json()

def post_like(job_id, feedback):
    return requests.post(f"{API_BASE}/likes/{job_id}", params={"feedback": feedback})