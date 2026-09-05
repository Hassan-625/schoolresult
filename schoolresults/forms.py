from django import forms
from .models import OfflineUpgradeRequest, Result, Student, Subject

class ResultForm(forms.ModelForm):
    class Meta:
        model = Result
        fields = ("student", "subject", "first_ca", "second_ca", "exam", "first_term", "second_term")
        widgets = {name: forms.NumberInput(attrs={"step":"0.01", "min":"0"}) for name in ("first_ca","second_ca","exam","first_term","second_term")}
    def __init__(self, *args, school=None, membership=None, **kwargs):
        super().__init__(*args, **kwargs)
        students=Student.objects.filter(school=school); self.fields["subject"].queryset=Subject.objects.filter(school=school)
        if membership and membership.role=="teacher": students=students.filter(class_level__in=membership.class_assignments.filter(can_enter_results=True).values("class_level"))
        self.fields["student"].queryset=students.order_by("class_level","last_name","first_name")
    def save(self,commit=True):
        result=super().save(False); result.school=result.student.school
        if commit: result.save()
        return result

class OfflineUpgradeForm(forms.ModelForm):
    class Meta:
        model=OfflineUpgradeRequest; fields=("target_tier","amount","proof_details"); widgets={"proof_details":forms.Textarea(attrs={"rows":4,"placeholder":"Bank reference, date, account name, and proof details"})}
