from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test

def is_stock(user):
    return user.department and user.department.code == 'STOCK'


from accounts.decorators import department_required



@login_required
@department_required("STOCK")
@user_passes_test(is_stock)
def dashboard(request):
    return render(request, 'stock/dashboard.html')
