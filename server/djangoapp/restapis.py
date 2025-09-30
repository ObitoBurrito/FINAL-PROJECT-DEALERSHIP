import os
import requests
from dotenv import load_dotenv
from urllib.parse import quote

load_dotenv()

backend_url = os.getenv('backend_url', default="http://localhost:3030")
sentiment_analyzer_url = os.getenv('sentiment_analyzer_url', default="http://localhost:5050/")

def get_request(endpoint, **kwargs):
    params = ""
    if kwargs:
        pairs = []
        for k, v in kwargs.items():
            pairs.append(f"{k}={v}")
        params = "&".join(pairs)

    if not endpoint.startswith("/"):
        endpoint = "/" + endpoint

    request_url = backend_url + endpoint
    if params:
        request_url = request_url + "?" + params

    print(f"GET from {request_url}")
    try:
        response = requests.get(request_url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as err:
        print(f"Network exception occurred: {err}")
        return None

def analyze_review_sentiments(text: str):
    """
    Calls the Code Engine sentiment microservice at:
    <sentiment_analyzer_url>/analyze/<text>
    """
    base = sentiment_analyzer_url
    if not base.endswith("/"):
        base = base + "/"

    to_send = text
    if " " in text and "%" not in text:
        to_send = quote(text, safe="")

    request_url = base + "analyze/" + to_send
    print(f"Sentiment GET from {request_url}")
    try:
        response = requests.get(request_url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as err:
        print(f"Unexpected error in analyze_review_sentiments: {err}")
        return None

def post_review(data_dict: dict):
    """
    Posts a review to the Node backend /insert_review endpoint.
    Expects a dict with keys like:
      name, dealership, review, purchase, purchase_date, car_make, car_model, car_year
    """
    request_url = backend_url + "/insert_review"
    print(f"POST to {request_url} with payload keys: {list(data_dict.keys())}")
    try:
        response = requests.post(request_url, json=data_dict, timeout=10)
        response.raise_for_status()
        print(response.json())
        return response.json()
    except Exception as err:
        print(f"Network exception occurred while posting review: {err}")
        return None
