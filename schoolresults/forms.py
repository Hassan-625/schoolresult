from django import forms
from .models import Result, Student

class ResultForm(forms.ModelForm):
    class Meta:
        model = Result
        fields = ("student", "subject", "first_ca", "second_ca", "exam", "first_term", "second_term")
        widgets = {name: forms.NumberInput(attrs={"step":"0.01", "min":"0"}) for name in ("first_ca","second_ca","exam","first_term","second_term")}
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["student"].queryset = Student.objects.order_by("class_level", "last_name", "first_name")
