# infilect-assignment

The api is deployed on https://infilect-assignment.herokuapp.com/
and required end-points are:
1. POST - https://infilect-assignment.herokuapp.com/v1/resources/login/
  Required cerendials { "username": "test-admin", "password" : "password.123" }
2. GET - https://infilect-assignment.herokuapp.com/v1/resources/logout/
  Required Bearer Token that is retrieved after loging in.
3. GET - https://infilect-assignment.herokuapp.com/v1/resources/weather/?page=1
  Required Bearer Token that is retrieved after loging in.
