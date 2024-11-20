from __future__ import absolute_import, unicode_literals

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")

import django
django.setup()


from celery import Celery
from celery.schedules import crontab
from celery.utils.log import get_task_logger
from django.conf import settings


app = Celery('app')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

logger = get_task_logger(__name__)

# Schedule for tasks
app.conf.beat_schedule = {
    'update_player_stats_weekly': {
        'task': 'core.tasks.update_player_stats',
        'schedule': crontab(minute='7')
    },
}
