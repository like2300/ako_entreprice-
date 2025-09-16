from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from accounts.decorators import department_required

def is_rh(user):
    return user.department and user.department.code == 'RH'

@login_required
@department_required("RH")
@user_passes_test(is_rh)
def dashboard(request):
    return render(request, 'rh/dashboard.html')
