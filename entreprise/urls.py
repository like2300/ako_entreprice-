from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),  # login, logout, signup, redirect
    path('stock/', include(('stock.urls', 'stock'), namespace='stock')),
    path('finance/', include(('finance.urls', 'finance'), namespace='finance')),
    path('rh/', include(('rh.urls', 'rh'), namespace='rh')),
]
# Gestion globale des erreurs
handler403 = "entreprise.views.custom_permission_denied"