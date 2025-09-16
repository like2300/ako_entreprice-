from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from accounts.decorators import department_required

def is_finance(user):
    return user.department and user.department.code == 'FIN'

@login_required
@department_required("FIN")
def dashboard(request):
    return render(request, 'finance/dashboard.html')
