from django.http import HttpResponseForbidden
from functools import wraps

def department_required(department_code):
    """
    Décorateur pour restreindre l'accès à un département précis.
    Exemple : @department_required("STOCK")
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return HttpResponseForbidden("⛔ Vous devez être connecté.")
            
            if not hasattr(request.user, "department") or request.user.department is None:
                return HttpResponseForbidden("⛔ Pas de département assigné.")
            
            if request.user.department.code != department_code:
                return HttpResponseForbidden("⛔ Vous n'avez pas accès à cette section.")
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

def user_is_active(view_func):
    """
    Décorateur pour vérifier si l'utilisateur est actif.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden("⛔ Vous devez être connecté.")
        
        if not request.user.is_active:
            return HttpResponseForbidden("⛔ Votre compte est désactivé.")
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view