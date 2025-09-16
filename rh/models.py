# rh/models.py
"""
Modèles RH de base :
- EmployeeProfile : informations RH rattachées à un utilisateur
- LeaveRequest : demande de congé simple
"""

from django.db import models
from django.conf import settings
from django.utils import timezone

LEAVE_STATUS = [
    ('PENDING', 'En attente'),
    ('APPROVED', 'Approuvé'),
    ('REJECTED', 'Rejeté'),
]

class EmployeeProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    position = models.CharField("Poste / Fonction", max_length=150, blank=True)
    phone = models.CharField("Téléphone", max_length=30, blank=True)
    address = models.TextField("Adresse", blank=True)
    hire_date = models.DateField("Date d'embauche", null=True, blank=True)
    is_active = models.BooleanField("Actif", default=True)
    created_at = models.DateTimeField("Créé le", default=timezone.now, editable=False)
    updated_at = models.DateTimeField("Mis à jour le", auto_now=True)

    class Meta:
        verbose_name = "Profil employé"
        verbose_name_plural = "Profils employés"
        ordering = ('user__username',)

    def __str__(self):
        return f"{self.user.username} — {self.position or '—'}"


class LeaveRequest(models.Model):
    employee = models.ForeignKey(EmployeeProfile, on_delete=models.CASCADE, related_name='leave_requests')
    start_date = models.DateField("Début")
    end_date = models.DateField("Fin")
    reason = models.TextField("Motif")
    status = models.CharField("Statut", max_length=10, choices=LEAVE_STATUS, default='PENDING')
    created_at = models.DateTimeField("Créé le", default=timezone.now, editable=False)
    updated_at = models.DateTimeField("Mis à jour le", auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Demande de congé"
        verbose_name_plural = "Demandes de congé"

    def __str__(self):
        return f"Congé {self.employee.user.username} ({self.start_date} → {self.end_date})"
