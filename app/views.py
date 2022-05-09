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

# List of cities
CITIES = ['Gwalior', 'London', 'New York', 'New Delhi', 'Mumbai', 'Kolkata', 'Chennai', 'Pune', 'Indore', 'Bhopal', 'Jabalpur', 'Surat', 'Varanasi', 'Allahabad', 'Lucknow', 'Chandigarh', 'Noida', 'Tokyo', 'California', 'Paris', 'Jaipur', 'Patna', 'Ranchi', 'Dhanbad', 'Haridwar', 'Hyderabad', 'Kochi', 'Goa', 'Rome', 'Munich']

class TokenAuthentication(TokenAuthentication):
    TokenAuthentication.keyword = "Bearer"

@api_view(["POST"])
@permission_classes([AllowAny])
def user_login(request):
    
    data = {}
    reqBody = json.loads(request.body)
    
    username = reqBody['username'] # Getting the username from the request body
    password = reqBody['password'] # Getting the password from the request body
    try:
        User = get_user_model() # getting the inbuilt user model
        
        Account = User.objects.get(username=username) # retreiving the user instance from the database
    except BaseException as e: # Rasing error in case the user instance cannot be retreived
        raise ValidationError({"400": f'{str(e)}'})

    token = Token.objects.get_or_create(user=Account)[0].key # Retreiving the token or creating token in case the token is not stored in database
    if not check_password(password, Account.password): # if password is incorrect raise the error with a message
        raise ValidationError({"message": "Incorrect Login credentials"})

    if not Account:
        raise ValidationError({"400": f'Account doesnt exist'})  # Raising error in case the account does not exists
    
    if not Account.is_active: # Raising Error in case the account is not active
        raise ValidationError({"400": f'Account not active'})
    
    # loging in the user with the given request and user instance
    login(request, Account)
    data["message"] = "user logged in"
    data["email_address"] = Account.email
    
    Res = {"data": data, "token": token}
    # Returning the response
    return Response(Res)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_logout(request):
    # Deleting the stored token from the database to logout him
    request.user.auth_token.delete()

    logout(request)

    return Response(data={"success": True, "message": "User logged out successfully"}, status=200)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_weather_details(request):
    page = int(request.GET.get('page'))-1 # Retrieving the page number to paginate the info
    
    redis_client = redis.Redis(host='redis-14419.c212.ap-south-1-1.ec2.cloud.redislabs.com', port=14419, password='RH4JPdiE5kBlwMY0WfIcgoHOW38wcFf2')

    for key in redis_client.scan_iter(): # Fetching the stored weather details of every city in the redis cloud server
        res.append(redis_client.json().get(key))
    redis_client.close()
    return Response(data = res[10*page:10*page+10]) # Returning the response as per the required page

# Created a thread that will fetch the weather details from the third party api in every 30 mins
# 
class WeatherRequest(Thread):
    def run(self):
        redis_client = redis.Redis(host='redis-14419.c212.ap-south-1-1.ec2.cloud.redislabs.com', port=14419, password='RH4JPdiE5kBlwMY0WfIcgoHOW38wcFf2')
        
        URL = "https://api.openweathermap.org/data/2.5/weather" # URL of the third party weather api
        PARAMS = {'appid':'432a2784d5ffb660d8a21fc122b8eed8'} # API-id for authenticity in weather api
        
        while(True):
            for city in CITIES:
                PARAMS['q'] = city
                r = requests.get(url= URL, params= PARAMS) # Fetching the results from the server for a specific city
                redis_client.json().set(str(city), Path.root_path(), r.json()) # storing the retreived data on a redis cloud server
            redis_client.close()

            sleep(30*60)    # Making the thread rest from next 30 mins

weather_details = WeatherRequest()
weather_details.start()
