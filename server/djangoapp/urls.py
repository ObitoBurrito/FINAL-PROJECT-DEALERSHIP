from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views

app_name = 'djangoapp'

urlpatterns = [
    # login API endpoint (POST)
    path(route='login', view=views.login_user, name='login'),
    # logout API endpoint (GET)
    path(route='logout', view=views.logout_user, name='logout'),
    # register API endpoint (POST)
    path(route='register', view=views.register_user, name='register'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
