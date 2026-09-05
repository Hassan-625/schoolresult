import re
from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP
from django.db import transaction
from django.db.models import Avg
from .models import Result, Student, grade_for

TWO = Decimal("0.01")
def q(value): return Decimal(value or 0).quantize(TWO, rounding=ROUND_HALF_UP)
def competition_positions(items, score):
    ordered = sorted(items, key=score, reverse=True); positions = {}; previous = object(); rank = 0
    for index, item in enumerate(ordered, 1):
        current = score(item)
        if current != previous: rank = index; previous = current
        positions[item.pk] = rank
    return positions

@transaction.atomic
def compute_class_results(class_level, term=None, session=None):
    students = Student.objects.filter(class_level=class_level)
    if term: students = students.filter(term=term)
    if session: students = students.filter(session=session)
    students = list(students.prefetch_related("results__subject"))
    if not students: return []
    class_size = len(students)
    totals = {}
    for student in students:
        rows = list(student.results.all()); total = sum((r.total for r in rows), Decimal("0"))
        totals[student.pk] = total
        student.total_score = q(total); student.average_score = q(total / len(rows)) if rows else Decimal("0")
        student.class_size = class_size; student.overall_grade = grade_for(student.average_score)
    ranks = competition_positions(students, lambda s: totals[s.pk])
    Student.objects.bulk_update([setattr(s, "position", ranks[s.pk]) or s for s in students], ["total_score","average_score","position","class_size","overall_grade"])
    by_subject = defaultdict(list)
    for student in students:
        for result in student.results.all(): by_subject[result.subject_id].append(result)
    updates = []
    for rows in by_subject.values():
        avg = q(sum((r.total for r in rows), Decimal("0")) / len(rows)); sranks = competition_positions(rows, lambda r: r.total)
        for row in rows: row.class_average = avg; row.subject_position = sranks[row.pk]; updates.append(row)
    Result.objects.bulk_update(updates, ["class_average", "subject_position"])
    return students

def safe_name(value): return re.sub(r"[^A-Za-z0-9._-]+", "_", value).strip("_")
