# rh/urls.py
from django.urls import path
from . import views

app_name = 'rh'

urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('employees/', views.employees, name='employees'),
    path('employees/create/', views.create_employee_profile, name='create_employee_profile'),
    path('employees/<int:user_id>/', views.get_employee_profile, name='get_employee_profile'),
    path('employees/<int:user_id>/delete/', views.delete_employee_profile, name='delete_employee_profile'),
    path('leave-requests/', views.leave_requests, name='leave_requests'),
    path('payroll/', views.payroll, name='payroll'),
    path('performance/', views.performance, name='performance'),
    path('recruitment/', views.recruitment, name='recruitment'),
]