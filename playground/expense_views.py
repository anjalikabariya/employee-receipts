from django.http import HttpResponse
from .models import Customer, Expense
from rest_framework.views import APIView
from datetime import date
from .utils import formate_date, validate_customer_id, get_monthly_expense, custom_range_total_expense, generate_report, check_user_session

class ExpenseView(APIView):
    def post(self, request, *args, **kwargs):
        # customer_id = check_user_session(request)    
        customer_id = request.data.get('customer_id')
        amount = request.data.get('amount')
        expense_ts = request.data.get('expense_ts')
        if expense_ts is None:
            expense_ts = date.today() 
        else:
            expense_ts = formate_date(expense_ts)
        data = {
            'customer': Customer.objects.get(customer_id=customer_id), 'amount': amount, 'created_at': expense_ts
        }
        try:
            Expense.objects.create(**data)
            response = 'success'
            status = 200
        except Exception as e:
            response = e
            status = 400
        return HttpResponse(response, status=status)

class CustomRangeExpense(APIView):
    def get(self, request, start_ts, end_ts):
        try:
            customer_id = check_user_session(request)    
        except AssertionError as e:
            return HttpResponse(e, status=404)

        custom_range_expense = custom_range_total_expense(customer_id, start_ts, end_ts)
        return HttpResponse(custom_range_expense['message'], status=custom_range_expense['status'])

class MonthlyExpense(APIView):
    def get(self, request, month, year):
        try:
            customer_id = check_user_session(request)    
        except AssertionError as e:
            return HttpResponse(e, status=404)

        if not validate_customer_id(customer_id):
            return HttpResponse('invalid customer_id', status=400)
        
        monthly_expense = get_monthly_expense(customer_id, month, year)
        if monthly_expense is not None:
            return HttpResponse(monthly_expense, status=200)
        return HttpResponse('No valid data present for given month and year', status=400)
    

class ExpenseReport(APIView):
    def get(self, request):
        try:
            customer_id = check_user_session(request)    
        except AssertionError as e:
            return HttpResponse(e, status=404)

        if not validate_customer_id(customer_id):
            return HttpResponse('invalid customer_id', status=400)
        report = generate_report(customer_id)

        return HttpResponse([report])