from django.contrib import admin, messages
from .models import (AttendanceRecord, CBTExam, ClassAssignment, Compilation, Expense, FeeRecord, OfflineUpgradeRequest, PayrollRecord, Result, ResultLock, School, SchoolMembership, Student, Subject, SubscriptionPayment)
from .tasks import compile_class_task

class TenantAdmin(admin.ModelAdmin):
    def get_queryset(self,request):
        qs=super().get_queryset(request)
        if request.user.is_superuser: return qs
        membership=request.user.school_memberships.filter(is_active=True).first()
        return qs.filter(school=membership.school) if membership else qs.none()
    def save_model(self,request,obj,form,change):
        if hasattr(obj,"school_id") and not obj.school_id and not request.user.is_superuser: obj.school=request.user.school_memberships.filter(is_active=True).first().school
        super().save_model(request,obj,form,change)

@admin.action(description="Compile selected students' classes")
def compile_selected(modeladmin,request,queryset):
    groups=set(queryset.values_list("school_id","class_level","term","session"))
    for school_id,class_level,term,session in groups: compile_class_task.delay(school_id,class_level,term,session)
    modeladmin.message_user(request,f"Queued {len(groups)} compilation job(s).",messages.SUCCESS)
@admin.register(Student)
class StudentAdmin(TenantAdmin):
    list_display=("full_name","school","reg_no","class_level","average_score","position"); list_filter=("school","class_level","term","session"); actions=(compile_selected,)
@admin.register(Result)
class ResultAdmin(TenantAdmin): list_display=("student","school","subject","total","grade","subject_position")
@admin.register(Subject)
class SubjectAdmin(TenantAdmin): list_display=("name","school","section","display_order")
@admin.register(Compilation)
class CompilationAdmin(TenantAdmin): list_display=("school","class_level","term","session","created_at")
@admin.register(School)
class SchoolAdmin(admin.ModelAdmin): list_display=("name","tier","subscription_status","subscription_expires_at","student_count")
@admin.register(SchoolMembership)
class MembershipAdmin(TenantAdmin): list_display=("user","school","role","is_active")
for model in [ClassAssignment,ResultLock,SubscriptionPayment,OfflineUpgradeRequest,FeeRecord,Expense,PayrollRecord,AttendanceRecord,CBTExam]: admin.site.register(model,TenantAdmin)
