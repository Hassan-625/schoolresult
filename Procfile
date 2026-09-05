web: gunicorn schoolresult.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120
worker: celery -A schoolresult worker -l info
beat: celery -A schoolresult beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
