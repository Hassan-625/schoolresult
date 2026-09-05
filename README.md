# schoolresult

Multi-tenant Nursery and Primary School Management SaaS built with Django 5.2, PostgreSQL/SQLite, OpenPyXL, Celery, Redis and django-celery-beat.

## SaaS architecture

- Shared database tenancy with school-scoped students, subjects, results, compilations, finance, attendance, payroll and CBT records.
- Global Django superusers operate the platform console at `/platform/`; school users receive a SchoolMembership role.
- Roles: Proprietor, Headmaster/Principal, Accountant and Teacher. Teacher academic access is restricted by ClassAssignment.
- Tiers are enforced server-side: Small (150 students), Mid (500), Premium (unlimited), with feature flags for broadsheets, SMS, fees, CBT, payroll, expenses and online payments.
- Subscription webhooks: `/webhooks/paystack/` and `/webhooks/flutterwave/`. Configure provider secrets with environment variables.
- Existing Excel templates remain immutable master files.

## Safe setup

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Do not delete `db.sqlite3` after real student/result data exists. Use migrations and backups.

## Compilation

```powershell
python manage.py compute_results
python manage.py compute_results "Basic 3"
python manage.py compute_results "Basic 3" --school highflyers
```

## Celery

```powershell
celery -A schoolresult worker -l info --pool=solo
celery -A schoolresult beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

Create end-of-term schedules in Admin > Periodic tasks. Choose `schoolresults.tasks.compile_all_results_task` and attach a configurable clocked/crontab schedule; no end-of-term date is hard-coded.
