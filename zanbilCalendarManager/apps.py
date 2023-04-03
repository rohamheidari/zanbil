from django.apps import AppConfig
import os


class zanbilCalendarManagerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'zanbilCalendarManager'

    def ready(self):
        from . import calendarmanager

        if os.environ.get('RUN_MAIN', None) != 'true':
            calendarmanager.attendedEventsChecker()
