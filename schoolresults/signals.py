from decimal import Decimal
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from .models import Result, Student, grade_for

def refresh_student(student_id):
    student=Student.objects.filter(pk=student_id).first()
    if not student: return
    rows=student.results.all(); count=rows.count(); total=sum((r.total for r in rows),Decimal("0")); average=total/count if count else 0
    Student.objects.filter(pk=student_id).update(total_score=total,average_score=average,overall_grade=grade_for(average))
@receiver(post_save, sender=Result)
def result_saved(sender, instance, **kwargs): refresh_student(instance.student_id)
@receiver(post_delete, sender=Result)
def result_deleted(sender, instance, **kwargs): refresh_student(instance.student_id)
