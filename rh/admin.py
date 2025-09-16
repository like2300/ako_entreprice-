# rh/admin.py
from django.contrib import admin
from .models import EmployeeProfile, LeaveRequest

@admin.register(EmployeeProfile)
class EmployeeProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'position', 'phone', 'is_active')
    search_fields = ('user__username', 'user__email', 'position', 'phone')
    list_filter = ('is_active',)
    readonly_fields = ('created_at', 'updated_at')

@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ('employee', 'start_date', 'end_date', 'status', 'created_at')
    search_fields = ('employee__user__username', 'reason')
    list_filter = ('status', 'start_date')
    readonly_fields = ('created_at', 'updated_at')
