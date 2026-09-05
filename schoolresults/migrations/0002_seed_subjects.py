from django.db import migrations

NURSERY = ["MATHEMATICS","ENGLISH LANGUAGE","HEALTH HABIT","SOCIAL HABIT","NURSERY SCIENCE","VERBAL REASONING","QUANTITATIVE REASONING","RHYMES","QUR'AN","ARABIC","CREATIVE ART","WRITING"]
PRIMARY = ["MATHEMATICS","ENGLISH LANGUAGE","HEALTH EDUCATION","SOCIAL STUDIES","BASIC SCIENCE","VERBAL REASONING","QUANTITATIVE REASONING","CIVIC EDUCATION","AGRICULTURAL SCIENCE","COMPUTER","QUR'AN","ARABIC","DRAWING","WRITING","ISLAMIC STUDIES"]

def seed(apps, schema_editor):
    Subject = apps.get_model("schoolresults", "Subject")
    for section, names in (("nursery", NURSERY), ("primary", PRIMARY)):
        for index, name in enumerate(names, 1):
            Subject.objects.get_or_create(name=name, section=section, defaults={"display_order":index})

class Migration(migrations.Migration):
    dependencies = [("schoolresults", "0001_initial")]
    operations = [migrations.RunPython(seed, migrations.RunPython.noop)]
