from decimal import Decimal
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

CLASS_CHOICES = [(x, x) for x in ["Pre-Nursery", "Nursery 1", "Nursery 2", "Nursery 3", "Basic 1", "Basic 2", "Basic 3", "Basic 4", "Basic 5"]]
TERM_CHOICES = [(x, x) for x in ["First", "Second", "Third"]]
SECTION_CHOICES = [("nursery", "Nursery"), ("primary", "Primary")]

def grade_for(score):
    score = Decimal(score or 0)
    return "A" if score >= 75 else "B" if score >= 65 else "C" if score >= 55 else "D" if score >= 45 else "E" if score >= 40 else "F"
def remark_for(grade):
    return {"A":"Excellent", "B":"Good", "C":"Average", "D":"Fair", "E":"Poor", "F":"Fail"}[grade]

class Subject(models.Model):
    name = models.CharField(max_length=100)
    section = models.CharField(max_length=10, choices=SECTION_CHOICES)
    display_order = models.PositiveSmallIntegerField(default=1)
    class Meta:
        ordering = ("section", "display_order", "name")
        constraints = [models.UniqueConstraint(fields=("name", "section"), name="unique_subject_per_section")]
    def __str__(self): return self.name

class Student(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="student_profile")
    first_name = models.CharField(max_length=80); last_name = models.CharField(max_length=80)
    reg_no = models.CharField(max_length=50, unique=True)
    class_level = models.CharField(max_length=20, choices=CLASS_CHOICES)
    department = models.CharField(max_length=100, blank=True); level = models.CharField(max_length=30, blank=True)
    term = models.CharField(max_length=10, choices=TERM_CHOICES)
    session = models.CharField(max_length=20, help_text="Example: 2026/2027")
    term_ending = models.DateField(); next_term_begins = models.DateField()
    total_score = models.DecimalField(max_digits=8, decimal_places=2, default=0, editable=False)
    average_score = models.DecimalField(max_digits=6, decimal_places=2, default=0, editable=False)
    position = models.PositiveIntegerField(null=True, blank=True, editable=False)
    class_size = models.PositiveIntegerField(default=0, editable=False)
    overall_grade = models.CharField(max_length=1, blank=True, editable=False)
    compiled_report = models.FileField(upload_to="results/individual/", blank=True, editable=False)
    class Meta: ordering = ("class_level", "last_name", "first_name")
    @property
    def full_name(self): return f"{self.first_name} {self.last_name}".strip()
    @property
    def section(self): return "nursery" if self.class_level == "Pre-Nursery" or self.class_level.startswith("Nursery") else "primary"
    def __str__(self): return f"{self.full_name} ({self.reg_no})"

class Result(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="results")
    subject = models.ForeignKey(Subject, on_delete=models.PROTECT, related_name="results")
    first_ca = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(20)])
    second_ca = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(20)])
    exam = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(60)])
    total = models.DecimalField(max_digits=5, decimal_places=2, default=0, editable=False)
    first_term = models.DecimalField(max_digits=5, decimal_places=2, default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    second_term = models.DecimalField(max_digits=5, decimal_places=2, default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    subject_average = models.DecimalField(max_digits=5, decimal_places=2, default=0, editable=False)
    grade = models.CharField(max_length=1, blank=True, editable=False); remark = models.CharField(max_length=20, blank=True, editable=False)
    subject_position = models.PositiveIntegerField(null=True, blank=True, editable=False)
    class_average = models.DecimalField(max_digits=5, decimal_places=2, default=0, editable=False)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ("subject__display_order", "subject__name")
        constraints = [models.UniqueConstraint(fields=("student", "subject"), name="unique_student_subject_result")]
    def clean(self):
        if self.student_id and self.subject_id and self.student.section != self.subject.section:
            raise ValidationError("The subject section must match the student's class section.")
    def save(self, *args, **kwargs):
        self.full_clean()
        self.total = self.first_ca + self.second_ca + self.exam
        self.subject_average = (self.total + self.first_term + self.second_term) / Decimal("3")
        self.grade = grade_for(self.total); self.remark = remark_for(self.grade)
        super().save(*args, **kwargs)
    def __str__(self): return f"{self.student} - {self.subject}"

def compilation_upload_path(instance, filename):
    import re
    clean = lambda value: re.sub(r"[^A-Za-z0-9._-]+", "_", value).strip("_")
    return f"results/{clean(instance.session)}/{instance.term}/{clean(instance.class_level)}/{filename}"

class Compilation(models.Model):
    class_level = models.CharField(max_length=20, choices=CLASS_CHOICES)
    term = models.CharField(max_length=10, choices=TERM_CHOICES); session = models.CharField(max_length=20)
    zip_file = models.FileField(upload_to=compilation_upload_path)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ("-created_at",)
    def __str__(self): return f"{self.class_level} {self.term} {self.session}"
