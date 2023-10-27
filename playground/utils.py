from datetime import datetime, date, timedelta
from django.db.models import Max, Min, Avg, Sum
from datetime import datetime, date, timedelta
from .models import Customer, Expense
from dateutil.relativedelta import relativedelta

def get_customer_data(email):
    customer_data = Customer.objects.filter(email=email).values()
    return customer_data

def check_user_session(request):
    customer_id = request.COOKIES.get('session_id')
    assert customer_id, "You need to log-in to access this functionality"
    return customer_id

def validate_customer_data(data):
    valid_age = True
    valid_gender = True
    valid_name = True
    genders = ['male', 'female', 'undefined']
    errors = []
    if not (data['age'] > 18 and data['age'] < 100):
        valid_age = False
        errors.append('Age should be within 18 and 100.')
    if data.get('gender') and not data['gender'] in genders:
        valid_gender = False
        errors.append('Gender should be either male, female, or undefined.')
    if not data['first_name'].isalpha():
        valid_name = False
        errors.append('Name should only contain alphabets.')
    
    valid = valid_age and valid_gender and valid_name
    
    return {'is_valid': valid, 'error': errors}

def formate_date(timestamp):
    date_format = '%Y-%m-%d'
    timestamp = datetime.strptime(timestamp, date_format).date()
    return timestamp

def get_monthly_expenses_between_dates(customer_id, start_date, end_date):
    current_date = start_date.replace(day=1)  # Set the start date to the first day of the month
    monthly_expenses = []

    while current_date <= end_date:
        month = current_date.month
        year = current_date.year

        expenses = get_monthly_expense(customer_id, month, year)
        monthly_expenses.append(expenses)

        # Move to the first day of the next month
        current_date = (current_date + relativedelta(months=1))

    return monthly_expenses

def get_monthly_expense(customer_id, month, year):
    monthly_expense = Expense.objects.filter(customer_id=customer_id, created_at__month=month, created_at__year=year).aggregate(total_sum=Sum('amount'))
    return monthly_expense['total_sum'] or 0

def validate_customer_id(customer_id):
    validate_id = Expense.objects.filter(customer_id=customer_id).values()
    return validate_id

def custom_range_total_expense(customer_id, start_ts, end_ts):
    if not validate_customer_id(customer_id):
        return {'message': 'invalid customer_id', 'status': 400}
    
    if start_ts and end_ts and (formate_date(start_ts) > formate_date(end_ts)):
        return {'message': 'start date should be smaller than end date', 'status': 400}
    
    if not start_ts or (formate_date(start_ts) > date.today()):
        return {'message': 'enter valid start time', 'status': 400}
    else:
        start_ts = formate_date(start_ts)

    if end_ts and (formate_date(end_ts) < date.today()):
        end_ts = formate_date(end_ts)
    else:
        end_ts = date.today()

    custom_range_expense = Expense.objects.filter(customer_id=customer_id, created_at__gte=start_ts, created_at__lte=end_ts).aggregate(total_sum=Sum('amount'))['total_sum']
    if custom_range_expense is not None:
        return {'message': custom_range_expense, 'status':200}
    return {'message': 'No valid data present for given month and year', 'status':400}
    
def generate_report(customer_id):
    report = {'all_time_avg': 0, 
                  'min_expense': 0,
                  'max_expense': 0,
                  'curr_year_total': 0,
                  'monthly_avg': 0
                  }
    report['all_time_avg'] = float(Expense.objects.filter(customer_id=customer_id).aggregate(avg=Avg('amount'))['avg'])
    report['max_expense'] = float(Expense.objects.filter(customer_id=customer_id).aggregate(max_expense=Max('amount'))['max_expense'])
    report['min_expense'] = float(Expense.objects.filter(customer_id=customer_id).aggregate(min_expense=Min('amount'))['min_expense'])
    report['curr_year_total'] = float(Expense.objects.filter(customer_id=customer_id, created_at__year=date.today().year).aggregate(total=Sum('amount'))['total'])
    first_entry = Expense.objects.filter(customer_id=customer_id).aggregate(min_start=Min('created_at'))['min_start']
    last_entry = Expense.objects.filter(customer_id=customer_id).aggregate(max_end=Max('created_at'))['max_end']
    if first_entry and last_entry:
        monthly_expenses = get_monthly_expenses_between_dates(customer_id, first_entry, last_entry)
        monthly_total=sum(monthly_expenses)
        report['monthly_avg'] = float(monthly_total/len(monthly_expenses))

    return report