from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from accounts.decorators import department_required, user_is_active
from .models import EmployeeProfile, LeaveRequest, Payroll, PerformanceReview, Recruitment
# ============================================================================= 
# user all get 
# =============================================================================
from accounts.models import *
# =============================================================================
# recupere le user presence 
# =============================================================================
from gestion_Horraire.models import PointageHoraire
from django.db.models import Sum, Count
from django.utils import timezone
from django.contrib import messages
from accounts.forms import CustomUserCreationForm 

# Import des fonctions pour les API AJAX
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

def get_today_attendance_stats():
    """Récupère les statistiques de présence pour aujourd'hui"""
    today = timezone.now().date()
    present_count = PointageHoraire.objects.filter(status='PRESENT', date=today).count()
    late_count = PointageHoraire.objects.filter(status='RETARD', date=today).count()
    
    # Calcul du taux de présence
    total_pointages = PointageHoraire.objects.filter(date=today).count()
    presence_percentage = (present_count / total_pointages * 100) if total_pointages > 0 else 0
    
    return {
        'presentCount': present_count,
        'lateCount': late_count,
        'presencePercentage': presence_percentage,
        'totalPointages': total_pointages
    }

def get_weekly_attendance_trend():
    """Récupère les tendances de présence sur 7 jours"""
    today = timezone.now().date()
    dates = [(today - timezone.timedelta(days=i)).strftime('%a') for i in range(6, -1, -1)]
    
    present_data = []
    absent_data = []
    
    for i in range(6, -1, -1):
        date = today - timezone.timedelta(days=i)
        present = PointageHoraire.objects.filter(status='PRESENT', date=date).count()
        absent = PointageHoraire.objects.filter(status='ABSENT', date=date).count()
        present_data.append(present)
        absent_data.append(absent)
    
    return {
        'labels': dates,
        'present_data': present_data,
        'absent_data': absent_data
    }

def get_employee_status_stats():
    """Récupère les statistiques par statut de contrat"""
    # Compter les employés par type de contrat
    contract_stats = EmployeeProfile.objects.values('contract_type').annotate(
        count=Count('contract_type')
    ).order_by()
    
    # Convertir en format utilisable pour le graphique
    labels = []
    data = []
    
    contract_mapping = {
        'CDI': 'CDI',
        'CDD': 'CDD',
        'Stage': 'Stage',
        'Alternance': 'Alternance',
        'Freelance': 'Freelance'
    }
    
    for stat in contract_stats:
        contract_type = stat['contract_type'] or 'Non défini'
        labels.append(contract_mapping.get(contract_type, contract_type))
        data.append(stat['count'])
    
    return {
        'labels': labels,
        'data': data
    }
@login_required
@department_required("RH")
def dashboard(request):
    # Statistiques de base
    employeeCount = CustomUser.objects.count()
    leaveCount = LeaveRequest.objects.filter(status='pending').count()
    
    # Statistiques de présence
    attendance_stats = get_today_attendance_stats()
    weekly_trend = get_weekly_attendance_trend()
    status_stats = get_employee_status_stats()
    
    # Paie du mois en cours
    current_month = timezone.now().replace(day=1)
    payroll_this_month = Payroll.objects.filter(month=current_month).count()
    
    # Récupérer les VRAIES activités récentes
    recent_activities = []
    
    # 1. Derniers pointages (5 derniers)
    recent_pointages = PointageHoraire.objects.select_related('employe').order_by('-date', '-heure_arrivee')[:5]
    for pointage in recent_pointages:
        recent_activities.append({
            'employee': pointage.employe.username,
            'datetime': f"{pointage.date} {pointage.heure_arrivee.strftime('%H:%M:%S') if pointage.heure_arrivee else ''}",
            'action': 'Pointage',
            'status': pointage.status,
            'type': 'pointage'
        })
    
    # 2. Dernières demandes de congé (5 dernières)
    recent_leaves = LeaveRequest.objects.select_related('employee').order_by('-created_at')[:5]
    for leave in recent_leaves:
        recent_activities.append({
            'employee': leave.employee.username,
            'datetime': leave.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'action': f'Demande de congé ({leave.get_leave_type_display()})',
            'status': leave.get_status_display(),
            'type': 'congé'
        })
    
    # 3. Dernières évaluations de performance (5 dernières)
    recent_reviews = PerformanceReview.objects.select_related('employee').order_by('-review_date')[:5]
    for review in recent_reviews:
        recent_activities.append({
            'employee': review.employee.username,
            'datetime': review.review_date.strftime('%Y-%m-%d'),
            'action': 'Évaluation de performance',
            'status': f'Note: {review.overall_rating}/5',
            'type': 'performance'
        })
    
    # 4. Derniers paiements de paie (5 derniers)
    recent_payrolls = Payroll.objects.select_related('employee').order_by('-month')[:5]
    for payroll in recent_payrolls:
        recent_activities.append({
            'employee': payroll.employee.username,
            'datetime': payroll.month.strftime('%Y-%m'),
            'action': 'Paiement de paie',
            'status': f'{payroll.total_salary} €',
            'type': 'paie'
        })
    
    # Trier toutes les activités par date (du plus récent au plus ancien)
    recent_activities.sort(key=lambda x: x['datetime'], reverse=True)
    
    # Garder seulement les 10 activités les plus récentes
    recent_activities = recent_activities[:10]
    
    context = {
        'employeeCount': employeeCount,
        'leaveCount': leaveCount,
        'payroll_this_month': payroll_this_month,
        'recent_activities': recent_activities,
        **attendance_stats,  # Décompresse toutes les stats de présence
        'weekly_trend': weekly_trend,
        'status_stats': status_stats,
    }
    
    return render(request, 'rh/dashboard.html', context)





@login_required
@department_required("RH")
def employees(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                messages.success(request, f'Employé {user.username} créé avec succès.')
                return redirect('rh:employees')
            except Exception as e:
                messages.error(request, f'Erreur lors de la création de l\'employé: {str(e)}')
        else:
            messages.error(request, 'Veuillez corriger les erreurs dans le formulaire.')
    else:
        form = CustomUserCreationForm()
    
    # Récupérer les utilisateurs avec leurs profils RH
    employees = CustomUser.objects.select_related('employee_profile', 'department').all()
    
    # Récupérer tous les utilisateurs et départements pour le modal
    all_users = CustomUser.objects.all()
    all_departments = Department.objects.all()
    
    # Identifier les utilisateurs sans profil employé
    users_without_profile = CustomUser.objects.filter(employee_profile__isnull=True)
    
    return render(request, 'rh/employees.html', {
        'employees': employees, 
        'form': form,
        'users': all_users,  # Pour le select des utilisateurs
        'departments': all_departments,  # Pour le select des départements
        'users_without_profile': users_without_profile  # Pour le bouton de création de profil
    })

@csrf_exempt
@require_http_methods(["POST"])
@login_required
@department_required("RH")
def create_employee_profile(request):
    """Créer un profil employé via AJAX"""
    try:
        data = json.loads(request.body)
        
        # Validation des données requises
        if not data.get('employee_id') or not data.get('user_id'):
            return JsonResponse({'success': False, 'error': 'Matricule et utilisateur sont requis'})
        
        user = CustomUser.objects.get(id=data['user_id'])
        
        # Créer ou mettre à jour le profil employé
        employee_profile, created = EmployeeProfile.objects.get_or_create(
            user=user,
            defaults={
                'employee_id': data['employee_id'],
                'position': data.get('position', ''),
                'department_id': data.get('department_id'),
                'hire_date': data.get('hire_date'),
                'contract_type': data.get('contract_type'),
                'salary': data.get('salary'),
                'is_active': data.get('status', 'true') == 'true'
            }
        )
        
        if not created:
            # Mise à jour du profil existant
            employee_profile.employee_id = data['employee_id']
            employee_profile.position = data.get('position', '')
            if data.get('department_id'):
                employee_profile.department_id = data.get('department_id')
            if data.get('hire_date'):
                employee_profile.hire_date = data.get('hire_date')
            employee_profile.contract_type = data.get('contract_type')
            if data.get('salary'):
                employee_profile.salary = data.get('salary')
            employee_profile.is_active = data.get('status', 'true') == 'true'
            employee_profile.save()
        
        return JsonResponse({'success': True, 'message': 'Profil employé créé avec succès'})
        
    except CustomUser.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Utilisateur non trouvé'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@require_http_methods(["GET"])
@login_required
@department_required("RH")
def get_employee_profile(request, user_id):
    """Récupérer les données d'un profil employé via AJAX"""
    try:
        employee_profile = EmployeeProfile.objects.get(user_id=user_id)
        
        data = {
            'employee_id': employee_profile.employee_id,
            'position': employee_profile.position or '',
            'department_id': employee_profile.department_id if employee_profile.department else '',
            'hire_date': employee_profile.hire_date.strftime('%Y-%m-%d') if employee_profile.hire_date else '',
            'contract_type': employee_profile.contract_type or '',
            'salary': str(employee_profile.salary) if employee_profile.salary else '',
            'status': 'true' if employee_profile.is_active else 'false'
        }
        
        return JsonResponse({'success': True, 'data': data})
        
    except EmployeeProfile.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Profil employé non trouvé'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@require_http_methods(["POST"])
@login_required
@department_required("RH")
def delete_employee_profile(request, user_id):
    """Supprimer un profil employé via AJAX"""
    try:
        employee_profile = EmployeeProfile.objects.get(user_id=user_id)
        employee_profile.delete()
        
        return JsonResponse({'success': True, 'message': 'Profil employé supprimé avec succès'})
        
    except EmployeeProfile.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Profil employé non trouvé'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@department_required("RH")
def leave_requests(request):
    leaves = LeaveRequest.objects.select_related('employee').all()
    
    # Filtrage
    status = request.GET.get('status')
    employee = request.GET.get('employee')
    leave_type = request.GET.get('leave_type')
    
    if status:
        leaves = leaves.filter(status=status)
    if employee:
        leaves = leaves.filter(employee_id=employee)
    if leave_type:
        leaves = leaves.filter(leave_type=leave_type)
    
    return render(request, 'rh/leave_requests.html', {'leaves': leaves})

@login_required
@department_required("RH")
def payroll(request):
    payrolls = Payroll.objects.select_related('employee').all()
    
    # Filtrage
    month = request.GET.get('month')
    employee = request.GET.get('employee')
    status = request.GET.get('status')
    
    if month:
        year, month_num = month.split('-')
        payrolls = payrolls.filter(month__year=year, month__month=month_num)
    if employee:
        payrolls = payrolls.filter(employee_id=employee)
    if status:
        if status == 'paid':
            payrolls = payrolls.exclude(paid_date__isnull=True)
        elif status == 'pending':
            payrolls = payrolls.filter(paid_date__isnull=True)
    
    return render(request, 'rh/payroll.html', {'payrolls': payrolls})

@login_required
@department_required("RH")
def performance(request):
    reviews = PerformanceReview.objects.select_related('employee', 'reviewer').all()
    
    # Filtrage
    employee = request.GET.get('employee')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    rating = request.GET.get('rating')
    
    if employee:
        reviews = reviews.filter(employee_id=employee)
    if start_date:
        reviews = reviews.filter(review_date__gte=start_date)
    if end_date:
        reviews = reviews.filter(review_date__lte=end_date)
    if rating:
        if rating == '4.5':
            reviews = reviews.filter(overall_rating__gte=4.5)
        elif rating == '4.0':
            reviews = reviews.filter(overall_rating__gte=4.0, overall_rating__lt=4.5)
        elif rating == '3.5':
            reviews = reviews.filter(overall_rating__gte=3.5, overall_rating__lt=4.0)
        elif rating == '3.0':
            reviews = reviews.filter(overall_rating__gte=3.0, overall_rating__lt=3.5)
        elif rating == '0':
            reviews = reviews.filter(overall_rating__lt=3.0)
    
    return render(request, 'rh/performance.html', {'reviews': reviews})

@login_required
@department_required("RH")
def recruitment(request):
    recruitments = Recruitment.objects.select_related('department').all()
    
    # Filtrage
    status = request.GET.get('status')
    department = request.GET.get('department')
    job_type = request.GET.get('job_type')
    
    if status:
        recruitments = recruitments.filter(status=status)
    if department:
        recruitments = recruitments.filter(department_id=department)
    if job_type:
        recruitments = recruitments.filter(job_type=job_type)
    
    return render(request, 'rh/recruitment.html', {'recruitments': recruitments})

def index(request):
    return render(request, 'rh/index.html')