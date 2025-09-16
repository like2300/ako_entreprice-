# stock/models.py
"""
Modèles liés au stock :
- StockItem : articles stockés
- StockMovement : historique des entrées/sorties (met à jour la quantité sur save())
"""

from django.db import models
from django.conf import settings
from django.utils import timezone

class StockItem(models.Model):
    name = models.CharField("Nom", max_length=255)
    sku = models.CharField("Référence (SKU)", max_length=100, unique=True)
    quantity = models.IntegerField("Quantité", default=0)
    unit_price = models.DecimalField("Prix unitaire", max_digits=12, decimal_places=2, null=True, blank=True)
    location = models.CharField("Emplacement", max_length=255, blank=True)
    description = models.TextField("Description", blank=True)
    is_active = models.BooleanField("Actif", default=True)
    created_at = models.DateTimeField("Créé le", default=timezone.now, editable=False)
    updated_at = models.DateTimeField("Mis à jour le", auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Article"
        verbose_name_plural = "Articles"

    def __str__(self):
        return f"{self.name} ({self.sku})"

    def adjust_quantity(self, delta):
        """
        Ajuste la quantité en mémoire et sauvegarde.
        Usage : item.adjust_quantity(+10) ou item.adjust_quantity(-5)
        Ne gère volontairement pas la logique métier complexe (réserves, validations).
        """
        self.quantity += int(delta)
        self.save(update_fields=['quantity'])


class StockMovement(models.Model):
    IN = 'IN'
    OUT = 'OUT'
    MOVEMENT_CHOICES = [
        (IN, 'Entrée'),
        (OUT, 'Sortie'),
    ]

    item = models.ForeignKey(StockItem, on_delete=models.CASCADE, related_name='movements')
    quantity = models.IntegerField("Quantité")
    movement_type = models.CharField("Type", max_length=3, choices=MOVEMENT_CHOICES)
    performed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    note = models.CharField("Note", max_length=255, blank=True)
    created_at = models.DateTimeField("Date", default=timezone.now, editable=False)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Mouvement de stock"
        verbose_name_plural = "Mouvements de stock"

    def __str__(self):
        actor = self.performed_by.username if self.performed_by else "système"
        return f"{self.get_movement_type_display()} {self.quantity} x {self.item.sku} ({actor})"

    def save(self, *args, **kwargs):
        """
        Lors de la création d'un mouvement on met à jour la quantité de l'article.
        ATTENTION : cette implémentation met à jour la quantité uniquement pour les nouveaux enregistrements.
        Si tu autorises l'édition des mouvements, il faudra gérer la correction (diff entre ancien et nouveau).
        """
        is_new = self._state.adding
        super().save(*args, **kwargs)
        if is_new:
            if self.movement_type == self.IN:
                self.item.quantity += self.quantity
            else:
                self.item.quantity -= self.quantity
            self.item.save()
