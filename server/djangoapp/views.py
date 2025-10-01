from django.http import JsonResponse
from django.contrib.auth import login, authenticate, logout
from django.views.decorators.csrf import csrf_exempt
import json
import logging
import urllib.parse

from .models import CarMake, CarModel
from .populate import initiate
from .restapis import get_request, analyze_review_sentiments, post_review

logger = logging.getLogger(__name__)

# ------------------------
# Auth Views
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
# Cars (admin helper)
# ------------------------

def get_cars(request):
    count = CarMake.objects.count()
    if count == 0:
        initiate()
    car_models = CarModel.objects.select_related('make')
    cars = []
    for car_model in car_models:
        cars.append({
            "CarModel": car_model.name,
            "CarMake": car_model.make.name
        })
    return JsonResponse({"CarModels": cars})

# ------------------------
# Dealership API
# ------------------------

def get_dealerships(request, state="All"):
    if state == "All":
        endpoint = "/fetchDealers"
    else:
        endpoint = "/fetchDealers/" + state
    dealerships = get_request(endpoint) or []
    return JsonResponse({"status": 200, "dealers": dealerships})


def get_dealer_details(request, dealer_id: int):
    endpoint = f"/fetchDealer/{dealer_id}"
    dealer = get_request(endpoint) or {}
    return JsonResponse({"status": 200, "dealer": dealer})


def get_dealer_reviews(request, dealer_id: int):
    endpoint = f"/fetchReviews/dealer/{dealer_id}"
    reviews = get_request(endpoint) or []

    enriched = []
    for r in reviews:
        review_text = r.get("review", "") or ""
        encoded = urllib.parse.quote(review_text, safe="")
        senti_resp = analyze_review_sentiments(encoded) or {}
        sentiment = (
            senti_resp.get("sentiment")
            or senti_resp.get("label")
            or senti_resp.get("sentiment_label")
            or "neutral"
        )
        review_detail = dict(r)
        review_detail["sentiment"] = sentiment
        enriched.append(review_detail)

    return JsonResponse({"status": 200, "reviews": enriched})

# ------------------------
# Add Review (POST)
# ------------------------

@csrf_exempt
def add_review(request):
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
