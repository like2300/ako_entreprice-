# finance/models.py
"""
Modèle minimaliste pour transactions financières.
- FinanceTransaction : enregistre paiements / mouvements financiers
"""

import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone

CURRENCIES = [
    ('XAF', 'FCFA (XAF)'),
    ('EUR', 'Euro (EUR)'),
    ('USD', 'Dollar (USD)'),
]

STATUS_CHOICES = [
    ('PENDING', 'En attente'),
    ('COMPLETED', 'Validé'),
    ('CANCELLED', 'Annulé'),
]

class FinanceTransaction(models.Model):
    reference = models.CharField("Référence", max_length=50, unique=True, editable=False)
    amount = models.DecimalField("Montant", max_digits=14, decimal_places=2)
    currency = models.CharField("Devise", max_length=4, choices=CURRENCIES, default='XAF')
    status = models.CharField("Statut", max_length=10, choices=STATUS_CHOICES, default='PENDING')
    description = models.TextField("Description", blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField("Date", default=timezone.now, editable=False)
    updated_at = models.DateTimeField("Mis à jour le", auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Transaction financière"
        verbose_name_plural = "Transactions financières"

    def __str__(self):
        return f"{self.reference} — {self.amount} {self.currency}"

    def save(self, *args, **kwargs):
        # Génère une référence courte si absent : TX-{uuid4 hex[:8]}
        if not self.reference:
            self.reference = f"TX-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def mark_completed(self):
        self.status = 'COMPLETED'
        self.save(update_fields=['status', 'updated_at'])
