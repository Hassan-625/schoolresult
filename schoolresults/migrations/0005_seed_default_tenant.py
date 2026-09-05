from django.db import migrations

def forwards(apps,schema_editor):
    School=apps.get_model("schoolresults","School"); Subject=apps.get_model("schoolresults","Subject"); Student=apps.get_model("schoolresults","Student"); Result=apps.get_model("schoolresults","Result"); Compilation=apps.get_model("schoolresults","Compilation")
    school,_=School.objects.get_or_create(slug="highflyers",defaults={"name":"Highflyers School","tier":"premium","subscription_status":"active"})
    Subject.objects.filter(school__isnull=True).update(school=school); Student.objects.filter(school__isnull=True).update(school=school); Result.objects.filter(school__isnull=True).update(school=school); Compilation.objects.filter(school__isnull=True).update(school=school)

class Migration(migrations.Migration):
    dependencies=[("schoolresults","0004_attendancerecord_cbtexam_classassignment_expense_and_more")]
    operations=[migrations.RunPython(forwards,migrations.RunPython.noop)]
