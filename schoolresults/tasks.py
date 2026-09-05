from celery import shared_task
from .excel import compile_class
from .models import CLASS_CHOICES

@shared_task
def compile_class_task(class_level, term=None, session=None):
    obj=compile_class(class_level,term,session); return obj.pk if obj else None
@shared_task
def compile_all_results_task():
    output = {}
    for name, _ in CLASS_CHOICES:
        compilation = compile_class(name)
        output[name] = compilation.pk if compilation else None
    return output
