from unfold.admin import ModelAdmin
from django.contrib import admin
from .models import EmployeeProfile, LeaveRequest, Payroll, PerformanceReview, Recruitment

# =============================================================================
# Admin pour EmployeeProfile
# =============================================================================
class EmployeeProfileAdmin(ModelAdmin):
    list_display = ('user', 'employee_id', 'department', 'position', 'hire_date', 'salary', 'is_active')
    list_filter = ('department', 'is_active')
    search_fields = ('user__username', 'employee_id', 'department__name', 'position')
    ordering = ('user__username', 'employee_id')
    
# =============================================================================
# Admin pour LeaveRequest
# =============================================================================
class LeaveRequestAdmin(ModelAdmin):
    list_display = ('employee', 'leave_type', 'start_date', 'end_date', 'reason', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at', 'updated_at')
    search_fields = ('employee__username', 'employee__employee_profile__employee_id', 'leave_type', 'reason')
    ordering = ('employee__username', 'employee__employee_profile__employee_id')

# =============================================================================
# Admin pour Payroll
# =============================================================================
class PayrollAdmin(ModelAdmin):
    list_display = ('employee', 'month', 'base_salary', 'bonuses', 'deductions', 'total_salary', 'paid_date')
    list_filter = ('month',)
    search_fields = ('employee__username', 'employee__employee_profile__employee_id', 'month')
    ordering = ('employee__username', 'employee__employee_profile__employee_id')

# =============================================================================
# Admin pour PerformanceReview
# =============================================================================
class PerformanceReviewAdmin(ModelAdmin):
    list_display = ('employee', 'review_date', 'period_start', 'period_end', 'overall_rating', 'comments')
    list_filter = ()
    search_fields = ('employee__username', 'employee__employee_profile__employee_id', 'comments')
    ordering = ('employee__username', 'employee__employee_profile__employee_id')

# =============================================================================
# Admin pour Recruitment
# =============================================================================
class RecruitmentAdmin(ModelAdmin):
    list_display = ('title', 'department', 'description', 'requirements', 'location', 'job_type', 'salary_range', 'posted_date', 'closing_date', 'status')
    list_filter = ('status',)
    search_fields = ('title', 'department__name', 'description', 'requirements', 'location', 'job_type', 'salary_range', 'posted_date', 'closing_date')
    ordering = ('title', 'department__name')

admin.site.register(EmployeeProfile, EmployeeProfileAdmin)
admin.site.register(LeaveRequest, LeaveRequestAdmin)
admin.site.register(Payroll, PayrollAdmin)
admin.site.register(PerformanceReview, PerformanceReviewAdmin)
admin.site.register(Recruitment, RecruitmentAdmin)