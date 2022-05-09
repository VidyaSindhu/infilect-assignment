import json
from threading import Thread
from time import sleep
import redis
from redis.commands.json.path import Path
from rest_framework.pagination import PageNumberPagination
from django.forms import ValidationError
from django.core.exceptions import ValidationError
from django.shortcuts import render
from rest_framework.response import Response
from django.contrib.auth import login, logout
from rest_framework.decorators import authentication_classes, permission_classes, api_view
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from django.contrib.auth.hashers import check_password
from rest_framework.authentication import TokenAuthentication
import requests
from django.core.paginator import Paginator
# Create your views here.

CITIES = ['Gwalior', 'London', 'New York', 'New Delhi', 'Mumbai', 'Kolkata', 'Chennai', 'Pune', 'Indore', 'Bhopal', 'Jabalpur', 'Surat', 'Varanasi', 'Allahabad', 'Lucknow', 'Chandigarh', 'Noida', 'Tokyo', 'California', 'Paris', 'Jaipur', 'Patna', 'Ranchi', 'Dhanbad', 'Haridwar', 'Hyderabad', 'Kochi', 'Goa', 'Rome', 'Munich']
class TokenAuthentication(TokenAuthentication):
    TokenAuthentication.keyword = "Bearer"

@api_view(["POST"])
@permission_classes([AllowAny])
def user_login(request):
    data = {}
    reqBody = json.loads(request.body)
    username = reqBody['username']
    password = reqBody['password']
    try:
        User = get_user_model()
        Account = User.objects.get(username=username)
    except BaseException as e:
        raise ValidationError({"400": f'{str(e)}'})

    token = Token.objects.get_or_create(user=Account)[0].key
    if not check_password(password, Account.password):
        raise ValidationError({"message": "Incorrect Login credentials"})

    if Account:
        if Account.is_active:
            login(request, Account)
            data["message"] = "user logged in"
            data["email_address"] = Account.email

            Res = {"data": data, "token": token}

            return Response(Res)

        else:
            raise ValidationError({"400": f'Account not active'})

    else:
        raise ValidationError({"400": f'Account doesnt exist'})

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_logout(request):

    request.user.auth_token.delete()

    logout(request)

    return Response(data={"success": True, "message": "User logged out successfully"}, status=200)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_weather_details(request):
    page = int(request.GET.get('page'))-1
    
    res = []
    redis_client = redis.Redis(host='localhost', port=6379, db=0)
    cities = []
    for key in redis_client.scan_iter():
        cities.append(key)
        res.append(redis_client.json().get(key))
    print(cities)
    redis_client.close()
    return Response(data = res[10*page:10*page+10])

class WeatherRequest(Thread):
    def run(self):
        redis_client = redis.Redis(host='localhost', port=6379, db=0)
        URL = "https://api.openweathermap.org/data/2.5/weather"
        PARAMS = {'appid':'432a2784d5ffb660d8a21fc122b8eed8'}
        while(True):
            for city in CITIES:
                PARAMS['q'] = city
                r = requests.get(url= URL, params= PARAMS)
                redis_client.json().set(str(city), Path.root_path(), r.json())
            redis_client.close()
            
            sleep(30*60)

weather_details = WeatherRequest()
weather_details.start()