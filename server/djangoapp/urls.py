from django.urls import path
from . import views

app_name = 'djangoapp'

urlpatterns = [
    # auth
    path('login', views.login_user, name='login'),
    path('logout', views.logout_user, name='logout'),

    # cars (admin data helper)
    path('get_cars', views.get_cars, name='getcars'),

    # dealerships
    path('get_dealers', views.get_dealerships, name='get_dealers'),
    path('get_dealers/<str:state>', views.get_dealerships, name='get_dealers_by_state'),

    # dealer details
    path('get_dealer/<int:dealer_id>', views.get_dealer_details, name='get_dealer'),

    # dealer reviews + sentiment
    path('get_dealer_reviews/<int:dealer_id>', views.get_dealer_reviews, name='get_dealer_reviews'),

    # add review (POST)
    path('add_review', views.add_review, name='add_review'),
]
