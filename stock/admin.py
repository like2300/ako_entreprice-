# stock/admin.py
from django.contrib import admin
from .models import StockItem, StockMovement

@admin.register(StockItem)
class StockItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'quantity', 'location', 'is_active')
    search_fields = ('name', 'sku')
    list_filter = ('is_active', 'location')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('name',)
    fieldsets = (
        (None, {
            'fields': ('name', 'sku', 'description', 'location', 'is_active')
        }),
        ('Stock & prix', {
            'fields': ('quantity', 'unit_price')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at')
        }),
    )

@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ('item', 'movement_type', 'quantity', 'performed_by', 'created_at')
    search_fields = ('item__name', 'item__sku', 'performed_by__username', 'note')
    list_filter = ('movement_type', 'created_at')
    readonly_fields = ('created_at',)
