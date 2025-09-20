from unfold.admin import ModelAdmin
from django.contrib import admin
from .models import PointageHoraire, LogConnexion, ParametresHoraires


@admin.register(PointageHoraire)
class PointageHoraireAdmin(ModelAdmin):
    list_display = ('employe', 'date', 'heure_arrivee', 'heure_depart', 'status', 'get_temps_travail_formate')
    list_filter = ('status', 'date')
    search_fields = ('employe__username', 'employe__first_name', 'employe__last_name')
    ordering = ('-date', '-heure_arrivee')
    readonly_fields = ('duree_travail_minutes', 'created_at', 'updated_at')
    list_per_page = 20
    date_hierarchy = 'date'

@admin.register(LogConnexion)
class LogConnexionAdmin(ModelAdmin):
    list_display = ('employe', 'date_heure', 'type_action', 'ip', 'device', 'success')
    list_filter = ('type_action', 'success', 'date_heure')
    search_fields = ('employe__username', 'ip', 'device')
    list_per_page = 20
    date_hierarchy = 'date_heure'

@admin.register(ParametresHoraires)
class ParametresHorairesAdmin(ModelAdmin):
    list_display = ('heure_debut_standard', 'heure_fin_standard', 'marge_retard', 'temps_pause_dejeuner')
    list_per_page = 20