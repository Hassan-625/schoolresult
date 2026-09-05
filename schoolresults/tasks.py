from celery import shared_task
from .excel import compile_class
from .models import CLASS_CHOICES, School

@shared_task
def compile_class_task(school_id, class_level, term=None, session=None):
    obj=compile_class(School.objects.get(pk=school_id),class_level,term,session); return obj.pk if obj else None
@shared_task
def compile_all_results_task(school_id=None):
    output = {}
    schools=School.objects.filter(pk=school_id) if school_id else School.objects.filter(subscription_status__in=[School.ACTIVE,School.TRIAL])
    for school in schools:
      for name, _ in CLASS_CHOICES:
        compilation = compile_class(school,name)
        output[f"{school.pk}:{name}"] = compilation.pk if compilation else None
    return output
