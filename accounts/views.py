from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm

def signup(request):
    """
    Formulaire d'inscription + connexion auto après création
    """
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # On crée l'utilisateur en base
            user = form.save()
            
            # On récupère username et password du formulaire
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password1")

            # On ré-authentifie proprement l'utilisateur
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)  # ici, pas besoin de forcer backend
                return redirect("accounts:redirect-after-login")
    else:
        form = CustomUserCreationForm()

    return render(request, "accounts/registration/register.html", {"form": form})


@login_required
def redirect_after_login(request):
    """
    Redirige l'utilisateur vers le bon espace en fonction de son département
    """
    user = request.user

    if user.department and user.department.code == "STOCK":
        return redirect("stock:dashboard")
    elif user.department and user.department.code == "FIN":
        return redirect("finance:dashboard")
    elif user.department and user.department.code == "RH":
        return redirect("rh:dashboard")
    
    # else:
    # # Admin ou user sans département → rediriger vers un dashboard générique
    #     return redirect("admin:index")  # ou une page d'accueil spécifique
    else:
        # Si pas de département -> on déconnecte pour éviter un accès sauvage
        from django.contrib.auth import logout
        logout(request)
        return redirect("accounts:login")
