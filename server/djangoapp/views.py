# Required imports
from django.http import JsonResponse
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)

# Handle login requests from the React frontend
@csrf_exempt
def login_user(request):
    """
    Expects JSON body: {"userName": "...", "password": "..."}
    On success: {"userName": "<name>", "status": "Authenticated"}
    On failure: {"userName": "<name>"} (frontend handles failed state)
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

# Handle logout requests
def logout_user(request):
    """
    GET /djangoapp/logout
    Returns: {"userName": ""} after session termination
    """
    logout(request)  # Terminate user session
    data = {"userName": ""}  # Return empty username
    return JsonResponse(data)

# Handle user registration requests
@csrf_exempt
def register_user(request):
    """
    POST /djangoapp/register
    Expects JSON body:
      {
        "userName": "...",
        "password": "...",
        "firstName": "...",
        "lastName": "...",
        "email": "..."
      }
    Behavior:
      - If username exists -> {"error": "Already Registered"}
      - Else create user, log them in -> {"userName": "<name>", "status": "Authenticated"}
    """
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body or "{}")
        username = data.get("userName", "").strip()
        password = data.get("password", "")
        first_name = data.get("firstName", "").strip()
        last_name = data.get("lastName", "").strip()
        email = data.get("email", "").strip()

        # Already registered?
        if User.objects.filter(username=username).exists():
            return JsonResponse({"error": "Already Registered"})

        # Create user
        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            first_name=first_name,
            last_name=last_name,
        )

        # Log them in
        login(request, user)
        return JsonResponse({"userName": username, "status": "Authenticated"})

    except json.JSONDecodeError:
        logger.exception("Invalid JSON in registration request")
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception:
        logger.exception("Unexpected error during registration")
        return JsonResponse({"error": "Unexpected error"}, status=500)

# Create a `logout_request` view to handle sign out request
# def logout_request(request):
# ...

# Create a `registration` view to handle sign up request
# @csrf_exempt
# def registration(request):
# ...

# # Update the `get_dealerships` view to render the index page with
# a list of dealerships
# def get_dealerships(request):
# ...

# Create a `get_dealer_reviews` view to render the reviews of a dealer
# def get_dealer_reviews(request,dealer_id):
# ...

# Create a `get_dealer_details` view to render the dealer details
# def get_dealer_details(request, dealer_id):
# ...

# Create a `add_review` view to submit a review
# def add_review(request):
# ...
