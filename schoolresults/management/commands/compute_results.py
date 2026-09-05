from django.core.management.base import BaseCommand, CommandError
from schoolresults.excel import compile_class
from schoolresults.models import CLASS_CHOICES
class Command(BaseCommand):
    help="Compute rankings and generate Excel/ZIP reports for every class or one class."
    def add_arguments(self,parser): parser.add_argument("class_level",nargs="?")
    def handle(self,*args,**options):
        classes=[x[0] for x in CLASS_CHOICES]; selected=options["class_level"]
        if selected and selected not in classes: raise CommandError(f"Unknown class: {selected}")
        for class_level in ([selected] if selected else classes):
            result=compile_class(class_level)
            self.stdout.write(self.style.SUCCESS(f"Compiled {class_level}: {result.zip_file.name}") if result else self.style.WARNING(f"Skipped {class_level}: no students"))
