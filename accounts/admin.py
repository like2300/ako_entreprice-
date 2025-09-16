from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Department
from .forms import CustomUserCreationForm, CustomUserChangeForm

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ['username', 'email', 'department', 'is_staff', 'is_active']
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('department',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('department',)}),
    )

admin.site.register(CustomUser, CustomUserAdmin)
