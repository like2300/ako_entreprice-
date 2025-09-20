# # rh/models.py
"""
Modèles RH de base :
- EmployeeProfile : informations RH rattachées à un utilisateur
- LeaveRequest : demande de congé simple
"""

from django.db import models
from django.conf import settings
from django.utils import timezone
from accounts.models import CustomUser, Department

class EmployeeProfile(models.Model):
    """Profil RH étendu pour un employé."""
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='employee_profile')
    employee_id = models.CharField(max_length=20, unique=True, verbose_name="Matricule")
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    position = models.CharField(max_length=100, blank=True, null=True, verbose_name="Poste")
    hire_date = models.DateField(null=True, blank=True, verbose_name="Date d'embauche")
    salary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Salaire")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    
    CONTRACT_TYPES = [
        ('CDI', 'CDI'),
        ('CDD', 'CDD'),
        ('Stage', 'Stage'),
        ('Alternance', 'Alternance'),
        ('Freelance', 'Freelance'),
    ]
    contract_type = models.CharField(max_length=20, choices=CONTRACT_TYPES, blank=True, null=True, verbose_name="Type de contrat")
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.employee_id}"

class LeaveRequest(models.Model):
    """Demande de congé."""
    REQUEST_TYPES = [
        ('paid', 'Congé payé'),
        ('unpaid', 'Congé sans solde'),
        ('sick', 'Congé maladie'),
        ('maternity', 'Congé maternité'),
        ('paternity', 'Congé paternité'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('approved', 'Approuvé'),
        ('rejected', 'Rejeté'),
    ]
    
    employee = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='leave_requests')
    leave_type = models.CharField(max_length=20, choices=REQUEST_TYPES, verbose_name="Type de congé")
    start_date = models.DateField(verbose_name="Date de début")
    end_date = models.DateField(verbose_name="Date de fin")
    reason = models.TextField(blank=True, null=True, verbose_name="Motif")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Statut")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date de mise à jour")
    
    def __str__(self):
        return f"{self.employee.username} - {self.leave_type} ({self.start_date} to {self.end_date})"
    
    @property
    def duration(self):
        """Calculate the duration of the leave in days."""
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days + 1
        return 0

class Payroll(models.Model):
    """Fiche de paie."""
    employee = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='payrolls')
    month = models.DateField(verbose_name="Mois")
    base_salary = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Salaire de base")
    bonuses = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Primes")
    deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Déductions")
    total_salary = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Salaire net")
    paid_date = models.DateField(null=True, blank=True, verbose_name="Date de paiement")
    
    def __str__(self):
        return f"{self.employee.username} - {self.month.strftime('%B %Y')}"

class PerformanceReview(models.Model):
    """Évaluation de performance."""
    employee = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='performance_reviews')
    reviewer = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='given_reviews')
    review_date = models.DateField(verbose_name="Date d'évaluation")
    period_start = models.DateField(verbose_name="Début de période")
    period_end = models.DateField(verbose_name="Fin de période")
    overall_rating = models.DecimalField(max_digits=3, decimal_places=2, verbose_name="Note globale")
    comments = models.TextField(blank=True, null=True, verbose_name="Commentaires")
    
    def __str__(self):
        return f"{self.employee.username} - {self.review_date}"

class Recruitment(models.Model):
    """Processus de recrutement."""
    JOB_TYPES = [
        ('full_time', 'Temps plein'),
        ('part_time', 'Temps partiel'),
        ('contract', 'Contrat'),
        ('internship', 'Stage'),
    ]
    
    STATUS_CHOICES = [
        ('open', 'Ouvert'),
        ('closed', 'Fermé'),
        ('filled', 'Pourvu'),
    ]
    
    title = models.CharField(max_length=200, verbose_name="Titre du poste")
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(verbose_name="Description")
    requirements = models.TextField(verbose_name="Prérequis")
    location = models.CharField(max_length=100, verbose_name="Lieu")
    job_type = models.CharField(max_length=20, choices=JOB_TYPES, verbose_name="Type de poste")
    salary_range = models.CharField(max_length=100, blank=True, null=True, verbose_name="Fourchette salariale")
    posted_date = models.DateField(auto_now_add=True, verbose_name="Date de publication")
    closing_date = models.DateField(null=True, blank=True, verbose_name="Date de clôture")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open', verbose_name="Statut")
    
    def __str__(self):
        return f"{self.title} - {self.department}"