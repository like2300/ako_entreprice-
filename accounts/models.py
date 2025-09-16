"""Custom user and Department model.

- Department: simple table to list departments (name + code)
- CustomUser: extends AbstractUser and adds a FK to Department so each user belongs to one department
"""
from django.db import models
from django.contrib.auth.models import AbstractUser

class Department(models.Model):
    # ex: name='Stock', code='STOCK'
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name

class CustomUser(AbstractUser):
    # Lien vers Department; SET_NULL pour garder utilisateur même si dept supprimé
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.username
