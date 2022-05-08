import imp
from django.urls import path
from django.urls.conf import include
from .views import get_weather_request, user_login, user_logout

urlpatterns = [
    path('login/', user_login),
    path('logout/', user_logout),
    path('weather/', get_weather_request),
]