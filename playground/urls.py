from django.urls import path
from . import customer_views, expense_views

urlpatterns = [
    path('customer', customer_views.CustomerView.as_view()),
    path('customer/sign-in', customer_views.SignIn.as_view()),
    path('customer/<str:email>', customer_views.CustomerView.as_view()),
    path('expenses/create', expense_views.ExpenseView.as_view()),
    path('expenses/user/<str:start_ts>/<str:end_ts>', expense_views.CustomRangeExpense.as_view()),
    path('expenses/user/monthly/<int:month>/<int:year>', expense_views.MonthlyExpense.as_view()),
    path('expenses/user/report', expense_views.ExpenseReport.as_view()),
]