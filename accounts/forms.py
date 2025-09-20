from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from accounts.models import CustomUser, Department, Profile
from rh.models import EmployeeProfile

class CustomUserCreationForm(UserCreationForm):
    department = forms.ModelChoiceField(queryset=Department.objects.all(), required=True)
    full_name = forms.CharField(max_length=150, required=True)
    date_of_birth = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    gender = forms.ChoiceField(choices=[("", "---------")] + Profile.GENDER_CHOICES, required=False)
    nationality = forms.CharField(max_length=50, required=False)
    marital_status = forms.CharField(max_length=20, required=False)
    address = forms.CharField(max_length=255, required=False)
    phone_number = forms.CharField(max_length=30, required=False)
    secondary_phone = forms.CharField(max_length=30, required=False)
    id_type = forms.ChoiceField(choices=[("", "---------")] + Profile.ID_TYPE_CHOICES, required=False)
    id_number = forms.CharField(max_length=100, required=False)
    id_issue_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    id_expiry_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    hire_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    contract_type = forms.ChoiceField(choices=[("", "---------")] + Profile.CONTRACT_TYPE_CHOICES, required=False)
    salary_base = forms.DecimalField(max_digits=10, decimal_places=2, required=False)
    manager_name = forms.CharField(max_length=100, required=False)
    position = forms.CharField(max_length=100, required=False)
    employee_id = forms.CharField(max_length=20, required=False)  # Rendu non obligatoire

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'department', 'full_name', 'date_of_birth', 'gender', 
                  'nationality', 'marital_status', 'address', 'phone_number', 'secondary_phone',
                  'id_type', 'id_number', 'id_issue_date', 'id_expiry_date', 'hire_date', 
                  'contract_type', 'salary_base', 'manager_name', 'position', 'employee_id')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.department = self.cleaned_data.get('department')
        if commit:
            user.save()
            # Create Profile only if it doesn't exist
            Profile.objects.get_or_create(
                user=user,
                defaults={
                    'full_name': self.cleaned_data.get('full_name'),
                    'date_of_birth': self.cleaned_data.get('date_of_birth'),
                    'gender': self.cleaned_data.get('gender'),
                    'nationality': self.cleaned_data.get('nationality'),
                    'marital_status': self.cleaned_data.get('marital_status'),
                    'address': self.cleaned_data.get('address'),
                    'phone_number': self.cleaned_data.get('phone_number'),
                    'secondary_phone': self.cleaned_data.get('secondary_phone'),
                    'id_type': self.cleaned_data.get('id_type'),
                    'id_number': self.cleaned_data.get('id_number'),
                    'id_issue_date': self.cleaned_data.get('id_issue_date'),
                    'id_expiry_date': self.cleaned_data.get('id_expiry_date'),
                    'hire_date': self.cleaned_data.get('hire_date'),
                    'contract_type': self.cleaned_data.get('contract_type'),
                    'salary_base': self.cleaned_data.get('salary_base'),
                    'manager_name': self.cleaned_data.get('manager_name')
                }
            )
            # Create EmployeeProfile only if employee_id is provided
            employee_id = self.cleaned_data.get('employee_id')
            if employee_id:
                EmployeeProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        'employee_id': employee_id,
                        'department': self.cleaned_data.get('department'),
                        'position': self.cleaned_data.get('position'),
                        'hire_date': self.cleaned_data.get('hire_date'),
                        'salary': self.cleaned_data.get('salary_base'),
                        'contract_type': self.cleaned_data.get('contract_type'),
                        'is_active': True
                    }
                )
        return user

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'department')