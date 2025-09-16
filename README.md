# Mini-projet Django — Entreprise (multi-départements)

Contenu:
- Projet Django `entreprise`
- Apps: accounts, stock, finance, rh
- Auth: CustomUser with `department` FK
- Signup & Login (single form)
- Redirection automatique selon department code (STOCK, FIN, RH)
- Fixtures to create departments

Instructions d'installation:

1. Créer un environnement virtuel (recommandé):
   python -m venv venv
   source venv/bin/activate   # macOS / Linux
   venv\Scripts\activate    # Windows (PowerShell)

2. Installer les dépendances:
   pip install -r requirements.txt

3. Appliquer les migrations:
   python manage.py makemigrations
   python manage.py migrate

4. Charger les départements (fixture fournie):
   python manage.py loaddata accounts/fixtures/departments.json

5. Créer un superuser (pour accéder à l'admin):
   python manage.py createsuperuser

6. Lancer le serveur:
   python manage.py runserver

Notes:
- Le projet utilise SQLite par défaut.
- Les templates sont basiques; adapte le HTML/CSS selon tes besoins.
- Pour ajouter un département, utilise l'admin ou charge une fixture.
