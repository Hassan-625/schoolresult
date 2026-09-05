# schoolresult

Nursery and Primary School Result Management System built with Django 5.2, SQLite, OpenPyXL, Celery, Redis and django-celery-beat.

## Windows setup (PowerShell)

Only use the removal commands below while intentionally rebuilding a disposable development database.

```powershell
cd schoolresult
Remove-Item .\db.sqlite3 -ErrorAction SilentlyContinue
Get-ChildItem .\schoolresults\migrations\*.py | Where-Object Name -ne '__init__.py' | Remove-Item
Get-ChildItem .\schoolresults\migrations\__pycache__ -ErrorAction SilentlyContinue | Remove-Item -Recurse
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py makemigrations schoolresults
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Do not delete `db.sqlite3` after real student/result data has been entered. Use normal migrations and backups.

## Compilation

```powershell
python manage.py compute_results
python manage.py compute_results "Basic 3"
```

## Celery and Redis

Start Redis (native, Docker, or WSL), then open separate terminals:

```powershell
celery -A schoolresult worker -l info --pool=solo
celery -A schoolresult beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

Create end-of-term schedules in Admin > Periodic tasks. Choose task `schoolresults.tasks.compile_all_results_task` and attach a configurable clocked/crontab schedule; no date is hard-coded.

## Initial subjects

Create subjects in Admin using the names already printed in each workbook. The generator matches by subject name and display order controls screen ordering.
