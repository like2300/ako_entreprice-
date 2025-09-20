from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages
from .models import PointageHoraire, LogConnexion, ParametresHoraires
from datetime import date
from accounts.decorators import user_is_active

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

# =============================================================================
# Views pour la page d'accueil de gestion_horraire
# =============================================================================

@login_required(login_url='accounts:login')
@user_is_active
def index(request): 
    return render(request, 'gestion_horraire/index.html')

# =============================================================================
# Views pour le pointage employe
# =============================================================================

@login_required(login_url='accounts:login')
@user_is_active
def pointage_employe(request):
    now = timezone.localtime(timezone.now())
    today = now.date()
    current_time = now.time()
    user = request.user

    # Récupération des paramètres horaires
    parametres = ParametresHoraires.objects.first()
    if not parametres:
        parametres = ParametresHoraires.objects.create()

    # Vérification si c'est un jour travaillé
    if not parametres.est_jour_travaille(today):
        messages.warning(request, "Ce jour n'est pas un jour travaillé.")
        est_jour_travaille = False
    else:
        est_jour_travaille = True

    # Récupération ou création du pointage
    pointage, created = PointageHoraire.objects.get_or_create(
        employe=user,
        date=today,
        defaults={
            'status': 'ABSENT'
        }
    )

    if request.method == 'POST':
        action = request.POST.get('action')
        
        if not est_jour_travaille:
            messages.error(request, "Impossible de pointer un jour non travaillé.")
            
        elif action == 'arrivee' and not pointage.heure_arrivee:
            # Récupérer l'heure exacte du serveur
            server_time_str = request.POST.get('server_time')
            if server_time_str:
                try:
                    h, m, s = map(int, server_time_str.split(':'))
                    pointage_time = now.replace(hour=h, minute=m, second=s).time()
                except (ValueError, TypeError):
                    pointage_time = current_time
            else:
                pointage_time = current_time

            # Vérifier si l'arrivée est après l'heure de fin standard
            if pointage_time >= parametres.heure_fin_standard:
                messages.error(request, "Impossible de pointer l'arrivée après l'heure de fin standard. Vous êtes considéré comme absent.")
                pointage.status = 'ABSENT'
                pointage.save()
                
                LogConnexion.objects.create(
                    employe=user,
                    type_action='POINTAGE_ARRIVEE',
                    ip=get_client_ip(request),
                    device=request.META.get('HTTP_USER_AGENT'),
                    success=False,
                    error="Arrivée après l'heure de fin",
                    details={
                        'heure_tentative': pointage_time.strftime('%H:%M:%S'),
                        'heure_fin_standard': parametres.heure_fin_standard.strftime('%H:%M:%S')
                    }
                )
            else:
                # Pointage normal
                retard_minutes = parametres.calculer_retard(pointage_time)
                pointage.heure_arrivee = pointage_time
                
                if retard_minutes > 0:
                    pointage.status = 'RETARD'
                    messages.warning(request, f"Retard de {retard_minutes} minutes enregistré.")
                else:
                    pointage.status = 'PRESENT'
                    messages.success(request, "Pointage d'arrivée enregistré à l'heure.")
                
                pointage.save()
                LogConnexion.objects.create(
                    employe=user,
                    type_action='POINTAGE_ARRIVEE',
                    ip=get_client_ip(request),
                    device=request.META.get('HTTP_USER_AGENT'),
                    details={
                        'retard_minutes': retard_minutes if retard_minutes > 0 else None,
                        'heure_exacte': pointage_time.strftime('%H:%M:%S')
                    }
                )
        
        elif action == 'depart':
            if not pointage.heure_arrivee:
                messages.error(request, "Vous devez d'abord pointer votre arrivée.")
            elif pointage.heure_depart:
                messages.error(request, "Vous avez déjà pointé votre départ aujourd'hui.")
            else:
                # Récupérer l'heure exacte
                server_time_str = request.POST.get('server_time')
                if server_time_str:
                    try:
                        h, m, s = map(int, server_time_str.split(':'))
                        pointage_time = now.replace(hour=h, minute=m, second=s).time()
                    except (ValueError, TypeError):
                        pointage_time = current_time
                else:
                    pointage_time = current_time

                # Vérifier si l'utilisateur essaie de pointer l'arrivée et le départ en même temps
                if pointage.heure_arrivee and pointage_time <= pointage.heure_arrivee:
                    messages.error(request, "L'heure de départ doit être après l'heure d'arrivée.")
                else:
                    pointage.heure_depart = pointage_time
                    pointage.save()
                    
                    pointage.refresh_from_db()
                    temps_travail_formate = pointage.get_temps_travail_formate()
                    
                    if pointage.status == 'ABSENT':
                        messages.warning(request, "Pointage enregistré mais statut marqué comme absent (arrivée trop tardive).")
                    else:
                        messages.success(request, f"Pointage de départ enregistré à {pointage_time.strftime('%H:%M')}. Temps de travail : {temps_travail_formate}")
                    
                    LogConnexion.objects.create(
                        employe=user,
                        type_action='POINTAGE_DEPART',
                        ip=get_client_ip(request),
                        device=request.META.get('HTTP_USER_AGENT'),
                        details={
                            'temps_travail': temps_travail_formate,
                            'heure_exacte': pointage_time.strftime('%H:%M:%S'),
                            'statut_final': pointage.status
                        }
                    )
            return redirect('gestion_Horraire:pointage_home')

    # Construction du contexte pour GET et POST
    context = {
        'pointage': pointage,
        'current_time': now,
        'parametres': parametres,
        'est_jour_travaille': est_jour_travaille,
        'peut_pointer_arrivee': est_jour_travaille and not pointage.heure_arrivee,
        'peut_pointer_depart': est_jour_travaille and pointage.heure_arrivee and not pointage.heure_depart,
    }
    return render(request, 'gestion_horraire/pointage_employe.html', context)

@login_required(login_url='accounts:login')
@user_is_active
def historique(request):
    from django.core.paginator import Paginator
    from django.db.models import Q, Avg, Count
    from datetime import datetime, timedelta

    # Récupération des paramètres de filtrage
    date_debut = request.GET.get('date_debut')
    date_fin = request.GET.get('date_fin')
    status = request.GET.get('status')

    # Construction de la requête de base
    pointages = PointageHoraire.objects.filter(employe=request.user)

    # Application des filtres
    if date_debut:
        try:
            date_debut = datetime.strptime(date_debut, '%Y-%m-%d').date()
            pointages = pointages.filter(date__gte=date_debut)
        except ValueError:
            pass

    if date_fin:
        try:
            date_fin = datetime.strptime(date_fin, '%Y-%m-%d').date()
            pointages = pointages.filter(date__lte=date_fin)
        except ValueError:
            pass

    if status:
        pointages = pointages.filter(status=status)

    # Calcul des statistiques
    stats = {
        'total_jours': pointages.count(),
        'retards': pointages.filter(status='RETARD').count(),
        'absences': pointages.filter(status='ABSENT').count(),
        'presences': pointages.filter(status='PRESENT').count(),
    }

    # Récupération des logs associés
    logs = LogConnexion.objects.filter(
        employe=request.user,
        type_action__in=['POINTAGE_ARRIVEE', 'POINTAGE_DEPART']
    ).order_by('-date_heure')[:10]

    # Tri final et pagination
    pointages = pointages.order_by('-date')
    paginator = Paginator(pointages, 10)  # 10 entrées par page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'stats': stats,
        'logs': logs,
        'filtres': {
            'date_debut': date_debut,
            'date_fin': date_fin,
            'status': status
        },
        'status_choices': PointageHoraire.STATUS_CHOICES
    }
    return render(request, 'gestion_horraire/historique.html', context)

@login_required(login_url='accounts:login')
@user_is_active
def profil(request):
    context = {
        'user': request.user,
    }
    return render(request, 'gestion_horraire/profil.html', context)