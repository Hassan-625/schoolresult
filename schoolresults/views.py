import json
from datetime import timedelta
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.db.models import Sum
from django.http import FileResponse, Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .forms import OfflineUpgradeForm, ResultForm
from .models import Compilation, OfflineUpgradeRequest, Result, School, Student, SubscriptionPayment
from .payments import apply_successful_payment, valid_flutterwave, valid_paystack
from .tasks import compile_class_task
from .tenancy import FEATURES, permission_required, teacher_class_allowed

def home(request): return render(request,"schoolresults/home.html")
def health(request): return JsonResponse({"status":"ok"})
@login_required
def dashboard(request):
    if request.user.is_superuser: return redirect("superadmin_dashboard")
    if hasattr(request.user,"student_profile"): return redirect("student_dashboard")
    if not request.school: raise PermissionDenied
    return render(request,"schoolresults/dashboard.html",{"student_count":request.school.students.count(),"result_count":request.school.results.count(),"compilations":request.school.compilations.all()[:5],"features":FEATURES[request.school.tier]})
@login_required
def student_dashboard(request):
    try: student=request.user.student_profile
    except Student.DoesNotExist: raise Http404("No student profile is linked to this account.")
    return render(request,"schoolresults/student_detail.html",{"student":student,"results":student.results.select_related("subject")})
@permission_required("students.read")
def student_list(request):
    qs=Student.objects.filter(school=request.school)
    if request.membership.role=="teacher": qs=qs.filter(class_level__in=request.membership.class_assignments.values("class_level"))
    return render(request,"schoolresults/student_list.html",{"students":qs})
@permission_required("academics.read")
def result_list(request):
    qs=Result.objects.filter(school=request.school).select_related("student","subject")
    if request.membership.role=="teacher": qs=qs.filter(student__class_level__in=request.membership.class_assignments.values("class_level"))
    return render(request,"schoolresults/result_list.html",{"results":qs})
@permission_required("academics.write")
def add_result(request):
    form=ResultForm(request.POST or None,school=request.school,membership=request.membership)
    if form.is_valid():
        student=form.cleaned_data["student"]
        if not teacher_class_allowed(request,student.class_level): raise PermissionDenied
        if request.school.result_locks.filter(class_level=student.class_level,term=student.term,session=student.session,is_locked=True).exists(): raise PermissionDenied("Results are locked for this term.")
        form.save(); messages.success(request,"Result saved."); return redirect("result_list")
    return render(request,"schoolresults/result_form.html",{"form":form,"title":"Enter result"})
@login_required
def student_detail(request,pk):
    if hasattr(request.user,"student_profile"): student=get_object_or_404(Student,pk=pk,user=request.user)
    else:
        if not request.school: raise Http404
        student=get_object_or_404(Student,pk=pk,school=request.school)
        if not request.user.is_superuser and not teacher_class_allowed(request,student.class_level): raise Http404
    return render(request,"schoolresults/student_detail.html",{"student":student,"results":student.results.select_related("subject")})
@permission_required("academics.read",feature="broadsheets")
def class_results(request,class_level):
    if not teacher_class_allowed(request,class_level): raise PermissionDenied
    return render(request,"schoolresults/class_results.html",{"class_level":class_level,"students":Student.objects.filter(school=request.school,class_level=class_level)})
@permission_required("results.approve",feature="broadsheets")
@require_POST
def trigger_compilation(request,class_level):
    compile_class_task.delay(request.school.pk,class_level); messages.success(request,f"Compilation queued for {class_level}."); return redirect("compiled_results")
@login_required
def download_student_report(request,pk):
    student=get_object_or_404(Student,pk=pk)
    if not request.user.is_superuser and student.user_id!=request.user.id and student.school_id!=getattr(request.school,"pk",None): raise Http404
    if not student.compiled_report: raise Http404("Report has not been compiled yet.")
    return FileResponse(student.compiled_report.open("rb"),as_attachment=True,filename=student.compiled_report.name.rsplit("/",1)[-1])
@permission_required("academics.read",feature="broadsheets")
def compiled_results(request): return render(request,"schoolresults/compiled_results.html",{"compilations":Compilation.objects.filter(school=request.school)})
@permission_required("subscription.manage")
def subscription(request): return render(request,"schoolresults/subscription.html",{"prices":settings.SUBSCRIPTION_PRICES,"features":FEATURES,"usage":request.school.students.count(),"limit":request.school.student_limit})
@permission_required("subscription.manage")
def offline_upgrade(request):
    form=OfflineUpgradeForm(request.POST or None)
    if form.is_valid():
        ticket=form.save(False); ticket.school=request.school; ticket.requested_by=request.user; ticket.save(); messages.success(request,"Upgrade request sent for review."); return redirect("subscription")
    return render(request,"schoolresults/offline_upgrade.html",{"form":form})
@user_passes_test(lambda u:u.is_superuser)
def superadmin_dashboard(request):
    return render(request,"schoolresults/superadmin_dashboard.html",{"schools":School.objects.all(),"payments":SubscriptionPayment.objects.select_related("school").order_by("-created_at")[:50],"tickets":OfflineUpgradeRequest.objects.select_related("school","requested_by").filter(status="pending"),"revenue":SubscriptionPayment.objects.filter(status="success").aggregate(total=Sum("amount"))["total"] or 0})
@user_passes_test(lambda u:u.is_superuser)
@require_POST
def school_action(request,pk):
    school=get_object_or_404(School,pk=pk); action=request.POST.get("action"); tier=request.POST.get("tier")
    if action in {School.ACTIVE,School.SUSPENDED,School.EXPIRED}: school.subscription_status=action
    if tier in dict(School.TIER_CHOICES): school.tier=tier
    school.save(); messages.success(request,f"{school.name} updated."); return redirect("superadmin_dashboard")
@user_passes_test(lambda u:u.is_superuser)
@require_POST
def approve_upgrade(request,pk):
    ticket=get_object_or_404(OfflineUpgradeRequest,pk=pk,status="pending"); ticket.status="approved"; ticket.reviewed_by=request.user; ticket.reviewed_at=timezone.now(); ticket.save()
    school=ticket.school; school.tier=ticket.target_tier; school.subscription_status=School.ACTIVE; school.subscription_expires_at=max(timezone.now(),school.subscription_expires_at or timezone.now())+timedelta(days=365); school.save()
    SubscriptionPayment.objects.create(school=school,provider="offline",reference=f"offline-{ticket.pk}",target_tier=ticket.target_tier,amount=ticket.amount,status="success",paid_at=timezone.now()); return redirect("superadmin_dashboard")
@csrf_exempt
@require_POST
def paystack_webhook(request):
    if not valid_paystack(request.body,request.headers.get("x-paystack-signature")): return HttpResponse(status=401)
    payload=json.loads(request.body); data=payload.get("data",{}); meta=data.get("metadata",{})
    if payload.get("event")=="charge.success": apply_successful_payment("paystack",data["reference"],int(meta["school_id"]),meta["target_tier"],data["amount"]/100,payload)
    return HttpResponse(status=200)
@csrf_exempt
@require_POST
def flutterwave_webhook(request):
    if not valid_flutterwave(request.headers.get("verif-hash")): return HttpResponse(status=401)
    payload=json.loads(request.body); data=payload.get("data",{}); meta=data.get("meta",{}) or data.get("metadata",{})
    if data.get("status")=="successful": apply_successful_payment("flutterwave",str(data["tx_ref"]),int(meta["school_id"]),meta["target_tier"],data["amount"],payload)
    return HttpResponse(status=200)
