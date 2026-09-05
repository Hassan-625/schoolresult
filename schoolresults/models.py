from decimal import Decimal
import re
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

CLASS_CHOICES=[(x,x) for x in ["Pre-Nursery","Nursery 1","Nursery 2","Nursery 3","Basic 1","Basic 2","Basic 3","Basic 4","Basic 5"]]
TERM_CHOICES=[(x,x) for x in ["First","Second","Third"]]
SECTION_CHOICES=[("nursery","Nursery"),("primary","Primary")]
def grade_for(score):
    score=Decimal(score or 0)
    return "A" if score>=75 else "B" if score>=65 else "C" if score>=55 else "D" if score>=45 else "E" if score>=40 else "F"
def remark_for(grade): return {"A":"Excellent","B":"Good","C":"Average","D":"Fair","E":"Poor","F":"Fail"}[grade]

class School(models.Model):
    SMALL,MID,PREMIUM="small","mid","premium"; TIER_CHOICES=[(SMALL,"Small"),(MID,"Mid-Tier"),(PREMIUM,"Premium")]
    ACTIVE,SUSPENDED,EXPIRED,TRIAL="active","suspended","expired","trial"; STATUS_CHOICES=[(ACTIVE,"Active"),(SUSPENDED,"Suspended"),(EXPIRED,"Expired"),(TRIAL,"Trial")]
    name=models.CharField(max_length=180); slug=models.SlugField(unique=True); email=models.EmailField(blank=True); phone=models.CharField(max_length=30,blank=True)
    tier=models.CharField(max_length=12,choices=TIER_CHOICES,default=SMALL); subscription_status=models.CharField(max_length=12,choices=STATUS_CHOICES,default=TRIAL)
    subscription_expires_at=models.DateTimeField(null=True,blank=True); created_at=models.DateTimeField(auto_now_add=True)
    @property
    def student_limit(self): return {self.SMALL:150,self.MID:500,self.PREMIUM:None}[self.tier]
    @property
    def student_count(self): return self.students.count()
    @property
    def subscription_is_valid(self): return self.subscription_status in {self.ACTIVE,self.TRIAL} and (not self.subscription_expires_at or self.subscription_expires_at>timezone.now())
    def __str__(self): return self.name

class SchoolMembership(models.Model):
    PROPRIETOR,HEADMASTER,ACCOUNTANT,TEACHER="proprietor","headmaster","accountant","teacher"
    ROLE_CHOICES=[(PROPRIETOR,"Proprietor / Owner"),(HEADMASTER,"Headmaster / Principal"),(ACCOUNTANT,"Accountant"),(TEACHER,"Teacher")]
    school=models.ForeignKey(School,on_delete=models.CASCADE,related_name="memberships"); user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="school_memberships")
    role=models.CharField(max_length=16,choices=ROLE_CHOICES); custom_permissions=models.JSONField(default=dict,blank=True); is_active=models.BooleanField(default=True); created_at=models.DateTimeField(auto_now_add=True)
    class Meta: constraints=[models.UniqueConstraint(fields=("school","user"),name="unique_school_membership")]
    def __str__(self): return f"{self.user} · {self.school} · {self.get_role_display()}"

class ClassAssignment(models.Model):
    school=models.ForeignKey(School,on_delete=models.CASCADE,related_name="class_assignments"); teacher=models.ForeignKey(SchoolMembership,on_delete=models.CASCADE,related_name="class_assignments",limit_choices_to={"role":"teacher"})
    class_level=models.CharField(max_length=20,choices=CLASS_CHOICES); can_enter_results=models.BooleanField(default=True); can_take_attendance=models.BooleanField(default=True)
    class Meta: constraints=[models.UniqueConstraint(fields=("school","teacher","class_level"),name="unique_teacher_class")]

class Subject(models.Model):
    school=models.ForeignKey(School,on_delete=models.CASCADE,related_name="subjects",null=True); name=models.CharField(max_length=100); section=models.CharField(max_length=10,choices=SECTION_CHOICES); display_order=models.PositiveSmallIntegerField(default=1)
    class Meta: ordering=("section","display_order","name"); constraints=[models.UniqueConstraint(fields=("school","name","section"),name="unique_school_subject_section")]
    def __str__(self): return self.name

class Student(models.Model):
    school=models.ForeignKey(School,on_delete=models.CASCADE,related_name="students",null=True); user=models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,blank=True,related_name="student_profile")
    first_name=models.CharField(max_length=80); last_name=models.CharField(max_length=80); reg_no=models.CharField(max_length=50); class_level=models.CharField(max_length=20,choices=CLASS_CHOICES)
    department=models.CharField(max_length=100,blank=True); level=models.CharField(max_length=30,blank=True); term=models.CharField(max_length=10,choices=TERM_CHOICES); session=models.CharField(max_length=20)
    term_ending=models.DateField(); next_term_begins=models.DateField(); total_score=models.DecimalField(max_digits=8,decimal_places=2,default=0,editable=False); average_score=models.DecimalField(max_digits=6,decimal_places=2,default=0,editable=False)
    position=models.PositiveIntegerField(null=True,blank=True,editable=False); class_size=models.PositiveIntegerField(default=0,editable=False); overall_grade=models.CharField(max_length=1,blank=True,editable=False); compiled_report=models.FileField(upload_to="results/individual/",blank=True,editable=False)
    class Meta: ordering=("class_level","last_name","first_name"); constraints=[models.UniqueConstraint(fields=("school","reg_no"),name="unique_school_registration")]
    @property
    def full_name(self): return f"{self.first_name} {self.last_name}".strip()
    @property
    def section(self): return "nursery" if self.class_level=="Pre-Nursery" or self.class_level.startswith("Nursery") else "primary"
    def clean(self):
        if self.school_id and not self.pk and self.school.student_limit is not None and self.school.students.count()>=self.school.student_limit: raise ValidationError({"school":f"Student limit reached for {self.school.get_tier_display()}. Upgrade to continue."})
    def save(self,*args,**kwargs): self.full_clean(); return super().save(*args,**kwargs)
    def __str__(self): return f"{self.full_name} ({self.reg_no})"

class Result(models.Model):
    school=models.ForeignKey(School,on_delete=models.CASCADE,related_name="results",null=True); student=models.ForeignKey(Student,on_delete=models.CASCADE,related_name="results"); subject=models.ForeignKey(Subject,on_delete=models.PROTECT,related_name="results")
    first_ca=models.DecimalField(max_digits=5,decimal_places=2,validators=[MinValueValidator(0),MaxValueValidator(20)]); second_ca=models.DecimalField(max_digits=5,decimal_places=2,validators=[MinValueValidator(0),MaxValueValidator(20)]); exam=models.DecimalField(max_digits=5,decimal_places=2,validators=[MinValueValidator(0),MaxValueValidator(60)])
    total=models.DecimalField(max_digits=5,decimal_places=2,default=0,editable=False); first_term=models.DecimalField(max_digits=5,decimal_places=2,default=0,validators=[MinValueValidator(0),MaxValueValidator(100)]); second_term=models.DecimalField(max_digits=5,decimal_places=2,default=0,validators=[MinValueValidator(0),MaxValueValidator(100)])
    subject_average=models.DecimalField(max_digits=5,decimal_places=2,default=0,editable=False); grade=models.CharField(max_length=1,blank=True,editable=False); remark=models.CharField(max_length=20,blank=True,editable=False); subject_position=models.PositiveIntegerField(null=True,blank=True,editable=False); class_average=models.DecimalField(max_digits=5,decimal_places=2,default=0,editable=False); updated_at=models.DateTimeField(auto_now=True)
    class Meta: ordering=("subject__display_order","subject__name"); constraints=[models.UniqueConstraint(fields=("school","student","subject"),name="unique_school_student_subject_result")]
    def clean(self):
        if self.student_id and self.subject_id and (self.student.school_id!=self.subject.school_id or self.school_id!=self.student.school_id): raise ValidationError("Student, subject and result must belong to the same school.")
        if self.student_id and self.subject_id and self.student.section!=self.subject.section: raise ValidationError("The subject section must match the student's class section.")
    def save(self,*args,**kwargs):
        if not self.school_id and self.student_id: self.school_id=self.student.school_id
        self.total=self.first_ca+self.second_ca+self.exam; self.subject_average=((self.total+self.first_term+self.second_term)/Decimal("3")).quantize(Decimal("0.01")); self.grade=grade_for(self.total); self.remark=remark_for(self.grade); self.full_clean(); return super().save(*args,**kwargs)
    def __str__(self): return f"{self.student} - {self.subject}"

def compilation_upload_path(instance,filename):
    clean=lambda v:re.sub(r"[^A-Za-z0-9._-]+","_",v).strip("_")
    return f"results/{instance.school.slug}/{clean(instance.session)}/{instance.term}/{clean(instance.class_level)}/{filename}"
class Compilation(models.Model):
    school=models.ForeignKey(School,on_delete=models.CASCADE,related_name="compilations",null=True); class_level=models.CharField(max_length=20,choices=CLASS_CHOICES); term=models.CharField(max_length=10,choices=TERM_CHOICES); session=models.CharField(max_length=20); zip_file=models.FileField(upload_to=compilation_upload_path); created_at=models.DateTimeField(auto_now_add=True)
    class Meta: ordering=("-created_at",)

class ResultLock(models.Model):
    school=models.ForeignKey(School,on_delete=models.CASCADE,related_name="result_locks"); class_level=models.CharField(max_length=20,choices=CLASS_CHOICES); term=models.CharField(max_length=10,choices=TERM_CHOICES); session=models.CharField(max_length=20); is_locked=models.BooleanField(default=False)
    class Meta: constraints=[models.UniqueConstraint(fields=("school","class_level","term","session"),name="unique_result_lock")]

class SubscriptionPayment(models.Model):
    school=models.ForeignKey(School,on_delete=models.CASCADE,related_name="subscription_payments"); provider=models.CharField(max_length=20); reference=models.CharField(max_length=150,unique=True); target_tier=models.CharField(max_length=12,choices=School.TIER_CHOICES); amount=models.DecimalField(max_digits=12,decimal_places=2); currency=models.CharField(max_length=5,default="NGN"); status=models.CharField(max_length=10,choices=[("pending","Pending"),("success","Successful"),("failed","Failed")],default="pending"); paid_at=models.DateTimeField(null=True,blank=True); metadata=models.JSONField(default=dict,blank=True); created_at=models.DateTimeField(auto_now_add=True)
class OfflineUpgradeRequest(models.Model):
    school=models.ForeignKey(School,on_delete=models.CASCADE,related_name="offline_upgrade_requests"); requested_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name="upgrade_requests"); target_tier=models.CharField(max_length=12,choices=School.TIER_CHOICES); amount=models.DecimalField(max_digits=12,decimal_places=2); proof_details=models.TextField(); status=models.CharField(max_length=10,choices=[("pending","Pending"),("approved","Approved"),("rejected","Rejected")],default="pending"); reviewed_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,blank=True,related_name="reviewed_upgrades"); created_at=models.DateTimeField(auto_now_add=True); reviewed_at=models.DateTimeField(null=True,blank=True)
class FeeRecord(models.Model):
    school=models.ForeignKey(School,on_delete=models.CASCADE,related_name="fees"); student=models.ForeignKey(Student,on_delete=models.CASCADE,related_name="fees"); description=models.CharField(max_length=150); amount_due=models.DecimalField(max_digits=12,decimal_places=2); amount_paid=models.DecimalField(max_digits=12,decimal_places=2,default=0); receipt_no=models.CharField(max_length=80,blank=True); paid_at=models.DateTimeField(null=True,blank=True); created_at=models.DateTimeField(auto_now_add=True)
class Expense(models.Model):
    school=models.ForeignKey(School,on_delete=models.CASCADE,related_name="expenses"); description=models.CharField(max_length=200); amount=models.DecimalField(max_digits=12,decimal_places=2); incurred_on=models.DateField(); recorded_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT); created_at=models.DateTimeField(auto_now_add=True)
class PayrollRecord(models.Model):
    school=models.ForeignKey(School,on_delete=models.CASCADE,related_name="payroll"); staff=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT); period=models.CharField(max_length=30); gross_amount=models.DecimalField(max_digits=12,decimal_places=2); net_amount=models.DecimalField(max_digits=12,decimal_places=2); paid_at=models.DateTimeField(null=True,blank=True)
class AttendanceRecord(models.Model):
    school=models.ForeignKey(School,on_delete=models.CASCADE,related_name="attendance"); student=models.ForeignKey(Student,on_delete=models.CASCADE,related_name="attendance"); date=models.DateField(); present=models.BooleanField(default=True); recorded_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT)
    class Meta: constraints=[models.UniqueConstraint(fields=("school","student","date"),name="unique_daily_attendance")]
class CBTExam(models.Model):
    school=models.ForeignKey(School,on_delete=models.CASCADE,related_name="cbt_exams"); title=models.CharField(max_length=150); class_level=models.CharField(max_length=20,choices=CLASS_CHOICES); is_published=models.BooleanField(default=False); starts_at=models.DateTimeField(); ends_at=models.DateTimeField()
