from django.contrib import admin, messages
from .models import Compilation, Result, Student, Subject
from .tasks import compile_class_task

@admin.action(description="Compile selected students' classes in background")
def compile_selected_classes(modeladmin, request, queryset):
    groups=set(queryset.values_list("class_level","term","session"))
    for class_level,term,session in groups: compile_class_task.delay(class_level,term,session)
    modeladmin.message_user(request,f"Queued {len(groups)} class compilation job(s).",messages.SUCCESS)
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display=("full_name","reg_no","class_level","term","session","average_score","position","class_size")
    list_filter=("class_level","term","session"); search_fields=("first_name","last_name","reg_no"); actions=(compile_selected_classes,)
@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display=("student","subject","total","grade","subject_position","class_average"); list_filter=("student__class_level","subject")
@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin): list_display=("name","section","display_order"); list_filter=("section",); ordering=("section","display_order")
@admin.register(Compilation)
class CompilationAdmin(admin.ModelAdmin): list_display=("class_level","term","session","created_at","zip_file"); readonly_fields=("created_at",)
