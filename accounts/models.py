"""Custom user and Department model.

- Department: simple table to list departments (name + code)
- CustomUser: extends AbstractUser and adds a FK to Department so each user belongs to one department
"""
from django.db import models
from django.contrib.auth.models import AbstractUser



# ============================================================================
# Ajoute des differents site
# ============================================================================
class Site(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.code})"




class Department(models.Model):
    # ex: name='Stock', code='STOCK'
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)



    def __str__(self):
        return self.name

class CustomUser(AbstractUser):
    
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    site = models.ForeignKey(Site, on_delete=models.SET_NULL, null=True, blank=True)
    # actif_user = models.BooleanField(default=True)
   
    def __str__(self):
        return self.username


# ============================================================================
# Profil utilisateur
# ============================================================================
class Profile(models.Model):
    GENDER_CHOICES = [
        ('M', 'Homme'),
        ('F', 'Femme'),
    ]
    
    ID_TYPE_CHOICES = [
        ('CNI', "Carte Nationale d'Identité"),
        ('Passeport', 'Passeport'),
        ('Permis', 'Permis de conduire'),
        ('Autre', 'Autre'),
    ]
    
    CONTRACT_TYPE_CHOICES = [
        ('CDI', 'CDI'),
        ('CDD', 'CDD'),
        ('Stage', 'Stage'),
        ('Interim', 'Intérim'),
        ('Consultant', 'Consultant'),
    ]
    
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='detailed_profile')
    full_name = models.CharField(max_length=150)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True)
    nationality = models.CharField(max_length=50, null=True, blank=True)
    marital_status = models.CharField(max_length=20, null=True, blank=True)
    photo = models.ImageField(upload_to='profiles/', null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    phone_number = models.CharField(max_length=30, null=True, blank=True)
    secondary_phone = models.CharField(max_length=30, null=True, blank=True)
    id_type = models.CharField(max_length=20, choices=ID_TYPE_CHOICES, null=True, blank=True)
    id_number = models.CharField(max_length=100, null=True, blank=True)
    id_issue_date = models.DateField(null=True, blank=True)
    id_expiry_date = models.DateField(null=True, blank=True)
    id_scan = models.FileField(upload_to='identity_docs/', null=True, blank=True)
    hire_date = models.DateField(null=True, blank=True)
    contract_type = models.CharField(max_length=20, choices=CONTRACT_TYPE_CHOICES, null=True, blank=True)
    salary_base = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    manager_name = models.CharField(max_length=100, null=True, blank=True)
    
    def __str__(self):
        return f"Profil de {self.user.username}"


# ============================================================================
# Ajoute de permition pour les utilisateurs 
# ============================================================================
class UserPermission(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="department_permissions")
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name="user_department_permissions")
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    def __str__(self):
        return f"Permissions de {self.user.username} pour {self.department.name}"