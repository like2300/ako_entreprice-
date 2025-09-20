from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password

class Command(BaseCommand):
    help = 'Créer un superutilisateur'

    def handle(self, *args, **options):
        User = get_user_model()
        
        # Vérifier si un superutilisateur existe déjà
        if User.objects.filter(is_superuser=True).exists():
            self.stdout.write(
                self.style.WARNING('Un superutilisateur existe déjà.')
            )
            return

        # Créer un superutilisateur
        username = 'admin'
        email = 'admin@example.com'
        password = 'admin123'
        
        User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        
        self.stdout.write(
            self.style.SUCCESS(f'Superutilisateur "{username}" créé avec succès.')
        )
        self.stdout.write(
            f'Identifiants:\n  Nom d\'utilisateur: {username}\n  Mot de passe: {password}'
        )