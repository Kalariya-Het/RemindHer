# import os
# from celery import Celery

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'RemindHer.settings')
# app = Celery('RemindHer')
# app.config_from_object('django.conf:settings', namespace='CELERY')
# app.autodiscover_tasks()

from celery import Celery

app = Celery('RemindHer', broker='redis://localhost:6379/0')

app.conf.update(
    result_expires=3600,
)

if __name__ == '__main__':
    app.start()
