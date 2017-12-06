import logging

from django.conf import settings

from .models import EventLog
from .helpers import conditions_evaluator


logger = logging.getLogger(__name__)


def sync_events_post_bulk_updates(input_queryset, additional_info={}):
    impacted_app = input_queryset.model._meta.app_label
    impacted_model = input_queryset.model.__name__
    tracked_fields = settings.EVENT_LOGGER_TRACKED_FIELDS[impacted_app][impacted_model].items()

    for impacted_object in input_queryset:
        for field_name, field_details in tracked_fields:
            to_update = conditions_evaluator(impacted_object, field_details.get("conditions"))
            if not to_update:
                continue
            last_update = EventLog.objects.filter(object_id=impacted_object.id,
                field_name=field_name, app_name=impacted_app, model_name=impacted_model).distinct('object_id').order_by('object_id', '-timestamp').first()
            latest_value = getattr(impacted_object, 'field', None)
            if last_update.after != latest_value:
                field_type = latest_value.__class__.__name__ if latest_value is not None else last_update.after.__class__.__name__
                data = {
                    'field_name': field_name,
                    'before': last_update.after,
                    'after': latest_value,
                    'column_type': field_type,
                    'model_name': impacted_model,
                    'app_name': impacted_app,
                    'object_id': impacted_object.id
                }
                data.update(additional_info)
                logger.debug(data)
                EventLog.objects.create(**data)
