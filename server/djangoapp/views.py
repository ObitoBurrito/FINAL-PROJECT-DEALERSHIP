# Uncomment the required imports before adding the code

# from django.shortcuts import render
# from django.http import HttpResponseRedirect, HttpResponse
# from django.contrib.auth.models import User
# from django.shortcuts import get_object_or_404, render, redirect
# from django.contrib.auth import logout
# from django.contrib import messages
# from datetime import datetime

from django.http import JsonResponse
from django.contrib.auth import login, authenticate, logout
import logging
import json
from django.views.decorators.csrf import csrf_exempt

# Cars (admin models) population/helpers
from .models import CarMake, CarModel
from .populate import initiate

# Back-end API helpers
from .restapis import get_request, analyze_review_sentiments, post_review

# For safe URL encoding when calling the sentiment service
import urllib.parse

# Get an instance of a logger
logger = logging.getLogger(__name__)

# ------------------------
# Auth views
# ------------------------

@csrf_exempt
def login_user(request):
    """Authenticate and log in a user; returns JSON with status."""
    try:
        data = json.loads(request.body)
    except Exception:
        return JsonResponse({"status": "Bad Request"}, status=400)

    username = data.get('userName', '')
    password = data.get('password', '')
    user = authenticate(username=username, password=password)
    if user is not None:
        login(request, user)
        return JsonResponse({"userName": username, "status": "Authenticated"})
    return JsonResponse({"userName": username, "status": "Unauthorized"}, status=401)


def logout_user(request):
    """Terminate session and return empty username JSON."""
    logout(request)
    return JsonResponse({"userName": ""})

# ------------------------
# Cars (admin) helper view
# ------------------------

def get_cars(request):
    """
    Populate on first call (if empty) and return CarMake/CarModel pairs.
    """
    count = CarMake.objects.filter().count()
    if count == 0:
        initiate()
    car_models = CarModel.objects.select_related('car_make')
    cars = []
    for car_model in car_models:
        cars.append({"CarModel": car_model.name, "CarMake": car_model.car_make.name})
    return JsonResponse({"CarModels": cars})

# ------------------------
# Dealership API views
# ------------------------

# Update the `get_dealerships` render list of dealerships all by default,
# particular state if state is passed
def get_dealerships(request, state="All"):
    if state == "All":
        endpoint = "/fetchDealers"
    else:
        endpoint = "/fetchDealers/" + state
    dealerships = get_request(endpoint) or []
    return JsonResponse({"status": 200, "dealers": dealerships})


def get_dealer_details(request, dealer_id: int):
    """
    Fetch a single dealer's details by id using /fetchDealer/<id>.
    """
    endpoint = f"/fetchDealer/{dealer_id}"
    dealer = get_request(endpoint) or {}
    return JsonResponse({"status": 200, "dealer": dealer})


def get_dealer_reviews(request, dealer_id: int):
    """
    Fetch reviews for a dealer using /fetchReviews/dealer/<id>.
    For each review, call the sentiment analyzer microservice and
    attach the 'sentiment' field (positive/neutral/negative).
    """
    endpoint = f"/fetchReviews/dealer/{dealer_id}"
    reviews = get_request(endpoint) or []

    enriched = []
    for r in reviews:
        # Safely extract the review text
        review_text = r.get("review", "") or ""
        # URL-encode to keep the microservice happy with spaces/special chars
        encoded = urllib.parse.quote(review_text, safe="")
        senti_resp = analyze_review_sentiments(encoded) or {}
        sentiment = (
            senti_resp.get("sentiment")
            or senti_resp.get("label")
            or senti_resp.get("sentiment_label")
            or "neutral"
        )
        review_detail = dict(r)  # copy original fields
        review_detail["sentiment"] = sentiment
        enriched.append(review_detail)

    return JsonResponse({"status": 200, "reviews": enriched})

# ------------------------
# Add Review (POST)
# ------------------------

@csrf_exempt
def add_review(request):
    """
    Accepts a JSON body (only for authenticated users) and posts it
    to the Node backend /insert_review endpoint via post_review().
    """
    if request.user.is_anonymous:
        return JsonResponse({"status": 403, "message": "Unauthorized"})

    try:
        data = json.loads(request.body)
    except Exception:
        return JsonResponse({"status": 400, "message": "Invalid JSON body"})

    try:
        response = post_review(data)
        if response is None:
            return JsonResponse({"status": 500, "message": "Error in posting review"})
        return JsonResponse({"status": 200, "message": "Review posted", "result": response})
    except Exception:
        return JsonResponse({"status": 401, "message": "Error in posting review"})
