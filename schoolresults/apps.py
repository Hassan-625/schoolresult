from django.apps import AppConfig
class SchoolresultsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "schoolresults"
    def ready(self):
        import schoolresults.signals  # noqa
