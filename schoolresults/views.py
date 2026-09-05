from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from .decorators import staff_required
from .forms import ResultForm
from .models import Compilation, Result, Student
from .tasks import compile_class_task

def home(request): return render(request,"schoolresults/home.html")
def health(request): return JsonResponse({"status":"ok"})
@login_required
def dashboard(request):
    if request.user.is_staff: return render(request,"schoolresults/dashboard.html",{"student_count":Student.objects.count(),"result_count":Result.objects.count(),"compilations":Compilation.objects.all()[:5]})
    return redirect("student_dashboard")
@login_required
def student_dashboard(request):
    try: student=request.user.student_profile
    except Student.DoesNotExist: raise Http404("No student profile is linked to this account.")
    return render(request,"schoolresults/student_detail.html",{"student":student,"results":student.results.select_related("subject")})
@staff_required
def student_list(request): return render(request,"schoolresults/student_list.html",{"students":Student.objects.all()})
@staff_required
def result_list(request): return render(request,"schoolresults/result_list.html",{"results":Result.objects.select_related("student","subject")})
@staff_required
def add_result(request):
    form=ResultForm(request.POST or None)
    if form.is_valid(): form.save(); messages.success(request,"Result saved."); return redirect("result_list")
    return render(request,"schoolresults/result_form.html",{"form":form,"title":"Enter result"})
@login_required
def student_detail(request,pk):
    student=get_object_or_404(Student,pk=pk)
    if not request.user.is_staff and student.user_id != request.user.id: raise Http404
    return render(request,"schoolresults/student_detail.html",{"student":student,"results":student.results.select_related("subject")})
@staff_required
def class_results(request,class_level): return render(request,"schoolresults/class_results.html",{"class_level":class_level,"students":Student.objects.filter(class_level=class_level)})
@staff_required
def trigger_compilation(request,class_level):
    if request.method=="POST": compile_class_task.delay(class_level); messages.success(request,f"Compilation queued for {class_level}.")
    return redirect("compiled_results")
@login_required
def download_student_report(request,pk):
    student=get_object_or_404(Student,pk=pk)
    if not request.user.is_staff and student.user_id != request.user.id: raise Http404
    if not student.compiled_report: raise Http404("Report has not been compiled yet.")
    return FileResponse(student.compiled_report.open("rb"),as_attachment=True,filename=student.compiled_report.name.rsplit("/",1)[-1])
@login_required
def compiled_results(request):
    qs=Compilation.objects.all() if request.user.is_staff else Compilation.objects.none()
    return render(request,"schoolresults/compiled_results.html",{"compilations":qs})
