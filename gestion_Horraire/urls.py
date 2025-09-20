from django.urls import path, include
from . import views

app_name = 'gestion_Horraire'

urlpatterns_pointage_employe = [
    path('home/', views.pointage_employe, name='pointage_home'),
]

urlpatterns = [
    path('', views.index, name='index'),
    path('pointage_employe/', include(urlpatterns_pointage_employe)),
    path('historique/', views.historique, name='historique'),
    path('profil/', views.profil, name='profil'),
]