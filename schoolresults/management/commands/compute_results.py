from django.core.management.base import BaseCommand, CommandError
from schoolresults.excel import compile_class
from schoolresults.models import CLASS_CHOICES, School
class Command(BaseCommand):
    help="Compute rankings and generate Excel/ZIP reports for every class or one class."
    def add_arguments(self,parser): parser.add_argument("class_level",nargs="?"); parser.add_argument("--school",dest="school_slug")
    def handle(self,*args,**options):
        classes=[x[0] for x in CLASS_CHOICES]; selected=options["class_level"]
        if selected and selected not in classes: raise CommandError(f"Unknown class: {selected}")
        schools=School.objects.filter(slug=options["school_slug"]) if options["school_slug"] else School.objects.all()
        if not schools.exists(): raise CommandError("No matching school. Use --school <slug>.")
        for school in schools:
          for class_level in ([selected] if selected else classes):
            result=compile_class(school,class_level)
            self.stdout.write(self.style.SUCCESS(f"Compiled {school}: {class_level}: {result.zip_file.name}") if result else self.style.WARNING(f"Skipped {school}: {class_level}: no students"))
