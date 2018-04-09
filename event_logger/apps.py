from django.apps import AppConfig

class EventLoggerConfig(AppConfig):
    name="event_logger"

    def ready(self):
        from event_logger import signals
