from django.shortcuts import render
from django.http import HttpResponse
from .models import Customer
from rest_framework.views import APIView
from .utils import get_customer_data, validate_customer_data

class CustomerView(APIView):
    def get(self, request, email):
        customer_data = get_customer_data(email)
        if not customer_data:
            return HttpResponse('No user with that email address exists.')
        return HttpResponse(customer_data)

    def post(self, request, *args, **kwargs):
        gender = request.data.get('gender')
        age = request.data.get('age')
        email = request.data['email']
        
        customer_data = get_customer_data(email)
        if customer_data:
            response = 'Email already in use'
            status = 400
            return HttpResponse(response, status=status)
        
        data = {
            'email': email,
            'first_name' : request.data['first_name'],
            'last_name' : request.data['last_name'],
            'password' : request.data['password'],
        }
        if age is not None:
            data.update(age=age)
        if gender:
            data.update(gender=gender)

        validation = validate_customer_data(data)
        if validation['is_valid']:
            try:
                Customer.objects.create(**data)
                response = Customer.objects.filter(email=email).values()
                status = 200
            except Exception as e: 
                print(e)
                response = 'Something went wrong'
                status = 500
        else:
            response = validation['error']
            status = 400

        return HttpResponse(response, status=status)

class SignIn(APIView):
    def post(self, request, *args, **kwargs):
        customer_data = Customer.objects.filter(email=request.data['email'], password=request.data['password']).values()
        if not customer_data:
            return HttpResponse("Wrong username and password", status=400)

        customer_id = customer_data[0]['customer_id']
        response = HttpResponse("Success", status=200)
        response.set_cookie('session_id', customer_id, max_age=10)
        return response
