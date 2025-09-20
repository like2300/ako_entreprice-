from unfold.admin import ModelAdmin
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Department , Profile, Site
from .forms import CustomUserCreationForm, CustomUserChangeForm

@admin.register(Department)
class DepartmentAdmin(ModelAdmin):
    list_display = ('name', 'code')
    list_per_page = 20

class CustomUserAdmin(UserAdmin, ModelAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ['username', 'email', 'department', 'is_staff', 'is_active']
    list_per_page = 20
    
    # Utiliser les fieldsets de base et y ajouter le champ 'department'
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'department')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'department', 'password1', 'password2'),
        }),
    )

admin.site.register(CustomUser, CustomUserAdmin)


# =============================================================================
# Ajoute du profil
# =============================================================================
class ProfileAdmin(ModelAdmin):
    list_display = ('user', 'full_name', 'date_of_birth', 'gender', 'nationality', 'marital_status', 'photo', 'address', 'phone_number', 'secondary_phone')
    list_per_page = 20

admin.site.register(Profile, ProfileAdmin)


# =============================================================================
# Ajoute du site
# =============================================================================
class SiteAdmin(ModelAdmin):
    list_display = ('name', 'code', 'address', 'city', 'country', 'latitude', 'longitude')
    list_per_page = 20

admin.site.register(Site, SiteAdmin)
