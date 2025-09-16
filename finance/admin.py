# finance/admin.py
from django.contrib import admin
from .models import FinanceTransaction

@admin.register(FinanceTransaction)
class FinanceTransactionAdmin(admin.ModelAdmin):
    list_display = ('reference', 'amount', 'currency', 'status', 'created_by', 'created_at')
    search_fields = ('reference', 'description', 'created_by__username')
    list_filter = ('currency', 'status', 'created_at')
    readonly_fields = ('reference', 'created_at', 'updated_at')
    ordering = ('-created_at',)
