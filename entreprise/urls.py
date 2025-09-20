from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(('accounts.urls', 'accounts'), namespace='accounts')),  # login, logout, signup, redirect
    path('stock/', include(('stock.urls', 'stock'), namespace='stock')),
    path('finance/', include(('finance.urls', 'finance'), namespace='finance')),
    path('resources_humaines/', include(('rh.urls', 'rh'), namespace='rh')),
    path('gestion_horraire/', include(('gestion_Horraire.urls', 'gestion_Horraire'), namespace='gestion_Horraire')),
]
# Gestion globale des erreurs
handler403 = "entreprise.views.custom_permission_denied"