from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from accounts.models import CustomUser

def default_jours_travailles():
    return {"1": True, "2": True, "3": True, "4": True, "5": True, "6": False, "7": False}

# =============================================================================
# Manager personnalisé pour simplifier les requêtes
# =============================================================================
class PointageManager(models.Manager):
    def aujourd_hui(self):
        """Retourne tous les pointages du jour"""
        return self.filter(date=timezone.now().date())

    def retards(self):
        """Retourne uniquement les employés en retard"""
        return self.filter(status='RETARD')

    def absents(self):
        """Retourne uniquement les employés absents"""
        return self.filter(status='ABSENT')

    def presents(self):
        """Retourne uniquement les employés présents"""
        return self.filter(status='PRESENT')


# =============================================================================
# Modèle de PointageHoraire
# =============================================================================
class PointageHoraire(models.Model):
    STATUS_CHOICES = [
        ('PRESENT', 'Présent'),
        ('ABSENT', 'Absent'),
        ('RETARD', 'En retard'),
        ('CONGE', 'En congé'),
    ]

    employe = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='pointages',
        verbose_name="Employé"
    )
    date = models.DateField(auto_now_add=True, verbose_name="Date de pointage")
    heure_arrivee = models.TimeField(null=True, blank=True, verbose_name="Heure d'arrivée")
    heure_depart = models.TimeField(null=True, blank=True, verbose_name="Heure de départ")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ABSENT', verbose_name="Statut")
    commentaire = models.TextField(null=True, blank=True, verbose_name="Commentaire")
    duree_travail_minutes = models.PositiveIntegerField(
        default=0,
        verbose_name="Durée de travail (minutes)",
        help_text="Stockée pour les rapports"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")

    objects = PointageManager()

    class Meta:
        verbose_name = "Pointage"
        verbose_name_plural = "Pointages"
        ordering = ['-date', '-heure_arrivee']
        unique_together = ['employe', 'date']
        indexes = [
            models.Index(fields=['employe', 'date']),
            models.Index(fields=['status']),
        ]

    def clean(self):
        super().clean()
        # Vérifier qu'un seul pointage existe par jour
        if PointageHoraire.objects.filter(employe=self.employe, date=self.date).exclude(pk=self.pk).exists():
            raise ValidationError("Un pointage existe déjà pour cet employé à cette date.")
        # Vérifier cohérence des heures
        if self.heure_arrivee and self.heure_depart:
            if self.heure_depart < self.heure_arrivee:
                raise ValidationError("L'heure de départ doit être après l'heure d'arrivée.")

    def save(self, *args, **kwargs):
        # Éviter les imports circulaires
        try:
            from .models import ParametresHoraires
            params = ParametresHoraires.objects.first()
            heure_limite = params.heure_debut_standard if params else timezone.datetime.strptime("09:00", "%H:%M").time()
            pause_dejeuner = params.temps_pause_dejeuner if params else 60
        except:
            heure_limite = timezone.datetime.strptime("09:00", "%H:%M").time()
            pause_dejeuner = 60

        # Mise à jour automatique du statut
        if self.heure_depart:
            # Déjà pointé le départ, statut définitif
            pass
        elif self.heure_arrivee:
            # Vérifier si l'arrivée est après l'heure de fin standard
            if params and self.heure_arrivee >= params.heure_fin_standard:
                # Arrivée après l'heure de fin standard = considéré comme retard
                self.status = 'RETARD'
            else:
                # Arrivée normale
                self.status = 'RETARD' if self.heure_arrivee > heure_limite else 'PRESENT'
        else:
            # Pas d'arrivée pointée
            self.status = 'ABSENT'

        # Calcul automatique de la durée de travail
        if self.heure_arrivee and self.heure_depart:
            arrivee_dt = timezone.datetime.combine(self.date, self.heure_arrivee)
            depart_dt = timezone.datetime.combine(self.date, self.heure_depart)
            
            if depart_dt < arrivee_dt:
                depart_dt += timezone.timedelta(days=1)
            
            duree_brute_minutes = int((depart_dt - arrivee_dt).total_seconds() // 60)
            
            if duree_brute_minutes >= pause_dejeuner:
                self.duree_travail_minutes = duree_brute_minutes - pause_dejeuner
            else:
                self.duree_travail_minutes = duree_brute_minutes
        else:
            self.duree_travail_minutes = 0

        self.full_clean()
        super().save(*args, **kwargs)

    def get_duree_travail(self):
        """Retourne la durée travaillée en timedelta"""
        return timedelta(minutes=self.duree_travail_minutes)
    
    def get_temps_travail(self):
        """Retourne la durée travaillée en timedelta (alias pour get_duree_travail)"""
        return self.get_duree_travail()
    
    def get_temps_travail_formate(self):
        """Retourne la durée travaillée formatée en heures et minutes"""
        duree_minutes = self.duree_travail_minutes
        heures, minutes = divmod(duree_minutes, 60)
        return f"{heures}h{minutes:02d}"

    def est_en_retard(self):
        """Retourne True si l'employé est en retard selon la configuration"""
        # Importer ici pour éviter les imports circulaires
        try:
            from .models import ParametresHoraires
            params = ParametresHoraires.objects.first()
            heure_limite = params.heure_debut_standard if params else timezone.datetime.strptime("09:00", "%H:%M").time()
        except:
            # En cas d'erreur, utiliser une valeur par défaut
            heure_limite = timezone.datetime.strptime("09:00", "%H:%M").time()
        return self.heure_arrivee and self.heure_arrivee > heure_limite

    def __str__(self):
        return f"{self.employe.username} - {self.date} ({self.get_status_display()})"


# =============================================================================
# Logs de Connexion
# =============================================================================
class LogConnexion(models.Model):
    TYPE_CHOICES = [
        ('LOGIN', 'Connexion'),
        ('LOGOUT', 'Déconnexion'),
        ('FAILED', 'Échec de connexion'),
        ('POINTAGE_ARRIVEE', 'Pointage arrivée'),
        ('POINTAGE_DEPART', 'Pointage départ'),
    ]

    employe = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='logs_connexion')
    date_heure = models.DateTimeField(auto_now_add=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    device = models.CharField(max_length=255, null=True, blank=True)
    type_action = models.CharField(max_length=50, choices=TYPE_CHOICES)
    details = models.JSONField(null=True, blank=True, help_text="Stockage de données supplémentaires au format JSON")
    success = models.BooleanField(default=True)
    error = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name = "Log de connexion"
        verbose_name_plural = "Logs de connexion"
        ordering = ['-date_heure']
        indexes = [
            models.Index(fields=['employe', 'date_heure']),
            models.Index(fields=['type_action']),
        ]

    def __str__(self):
        return f"{self.employe.username if self.employe else 'Inconnu'} - {self.date_heure:%Y-%m-%d %H:%M:%S} - {self.get_type_action_display()}"


# =============================================================================
# Paramètres des horaires
# =============================================================================
class ParametresHoraires(models.Model):
    heure_debut_standard = models.TimeField(default=timezone.datetime.strptime("09:00", "%H:%M").time())
    heure_fin_standard = models.TimeField(default=timezone.datetime.strptime("17:00", "%H:%M").time())
    marge_retard = models.IntegerField(default=15, help_text="Temps de grâce avant de considérer un retard (minutes)")
    temps_pause_dejeuner = models.IntegerField(default=60, help_text="Durée de la pause déjeuner (minutes)")
    jours_travailles = models.JSONField(
        default=default_jours_travailles,
        help_text="1=Lundi, 7=Dimanche"
    )

    class Meta:
        verbose_name = "Paramètres horaires"
        verbose_name_plural = "Paramètres horaires"

    def __str__(self):
        return f"Config horaire ({self.heure_debut_standard:%H:%M}-{self.heure_fin_standard:%H:%M})"

    def est_jour_travaille(self, date):
        """Vérifie si le jour donné est un jour travaillé"""
        return self.jours_travailles.get(str(date.isoweekday()), False)

    def calculer_retard(self, heure_arrivee):
        """Calcule le retard en minutes par rapport à l'heure standard"""
        if not heure_arrivee:
            return 0
        debut = timezone.datetime.combine(timezone.now().date(), self.heure_debut_standard)
        arrivee = timezone.datetime.combine(timezone.now().date(), heure_arrivee)
        difference = (arrivee - debut).total_seconds() / 60
        return max(0, difference - self.marge_retard)