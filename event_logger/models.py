from django.conf import settings
from django.db import models


class EventLog(models.Model):
    model_name = models.TextField()
    model_id = models.TextField()
    field_name = models.TextField()
    before = models.TextField(null=True)
    after = models.TextField(null=True)
    column_type = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    for additional_field in settings.EVENT_LOGGER_OUTPUT_FORMAT.get("columns", {}).keys():
        locals()[additional_field] = models.TextField(null=True)
