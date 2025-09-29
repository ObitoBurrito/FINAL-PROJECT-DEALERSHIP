from django.http import JsonResponse
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
import logging
import json

# NEW: models & populate import for get_cars
from .models import CarMake, CarModel
from .populate import initiate

logger = logging.getLogger(__name__)

@csrf_exempt
def login_user(request):
    """
    POST /djangoapp/login
    Body: {"userName":"...", "password":"..."}
    On success: {"userName":"<name>", "status":"Authenticated"}
    """
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body or "{}")
        username = data.get("userName", "")
        password = data.get("password", "")
        user = authenticate(username=username, password=password)
        resp = {"userName": username}
        if user is not None:
            login(request, user)
            resp["status"] = "Authenticated"
        return JsonResponse(resp)
    except json.JSONDecodeError:
        logger.exception("Invalid JSON in login request")
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception:
        logger.exception("Unexpected error during login")
        return JsonResponse({"error": "Unexpected error"}, status=500)

def logout_user(request):
    """
    GET /djangoapp/logout
    Returns {"userName": ""} after session termination.
    """
    logout(request)
    return JsonResponse({"userName": ""})

@csrf_exempt
def register_user(request):
    """
    POST /djangoapp/register
    Body: {
      "userName": "...",
      "password": "...",
      "firstName": "...",
      "lastName": "...",
      "email": "..."
    }
    - If user exists: {"error": "Already Registered"}
    - Else create, login, return {"userName":"<name>", "status":"Authenticated"}
    """
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body or "{}")
        username = (data.get("userName") or "").strip()
        password = data.get("password") or ""
        first_name = (data.get("firstName") or "").strip()
        last_name  = (data.get("lastName") or "").strip()
        email      = (data.get("email") or "").strip()

        if User.objects.filter(username=username).exists():
            return JsonResponse({"error": "Already Registered"})

        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            first_name=first_name,
            last_name=last_name,
        )
        login(request, user)
        return JsonResponse({"userName": username, "status": "Authenticated"})
    except json.JSONDecodeError:
        logger.exception("Invalid JSON in registration request")
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception:
        logger.exception("Unexpected error during registration")
        return JsonResponse({"error": "Unexpected error"}, status=500)

def get_cars(request):
    """
    GET /djangoapp/get_cars
    If no CarMake/CarModel exist, populate once, then return:
      {"CarModels": [{"CarModel": "<model>", "CarMake": "<make>"} ...]}
    """
    try:
        count = CarMake.objects.count()
        if count == 0:
            initiate()

        # Our CarModel FK is named 'make' (not 'car_make'), so select_related('make')
        car_models = CarModel.objects.select_related('make').all()

        cars = []
        for car_model in car_models:
            cars.append({
                "CarModel": car_model.name,
                "CarMake":  car_model.make.name
            })

        return JsonResponse({"CarModels": cars})
    except Exception as e:
        logger.exception("Error in get_cars")
        return JsonResponse({"error": "Failed to fetch cars"}, status=500)
