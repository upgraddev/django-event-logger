import logging

from django.conf import settings
from django.db.models.signals import pre_save
from django.dispatch.dispatcher import receiver

from .models import EventLog
from .helpers import conditions_evaluator


logger = logging.getLogger(__name__)


def additional_info_adder(data, original_object=None):
    for import_statement in settings.EVENT_LOGGER_OUTPUT_FORMAT.get("imports", []):
        exec(import_statement)
    for column_name, column_details in settings.EVENT_LOGGER_OUTPUT_FORMAT.get("columns", {}).items():
        column_value = column_details.get("default")
        if column_details.get("object_name") and column_details.get("property"):
            column_object = eval(column_details["object_name"])
            column_value = getattr(column_object, column_details["property"], column_value)
        data[column_name] = column_value


def create_signal_receiever(sender, tracked_fields, app_name=None):
    @receiver(pre_save, sender=sender)
    def track_field_changes(sender, instance, **kwargs):
        old_instance = sender.objects.get(id=instance.id)
        for field_name, field_details in tracked_fields.items():
            to_update = conditions_evaluator(old_instance, field_details.get("conditions"))
            if not to_update:
                continue
            prev_value = getattr(old_instance, field_name)
            new_value = getattr(instance, field_name)
            if prev_value != new_value:
                field_type = prev_value.__class__.__name__ if prev_value is not None else new_value.__class__.__name__
                data = {
                    'field_name': field_name,
                    'before': prev_value,
                    'after': new_value,
                    'column_type': field_type,
                    'model_name': sender.__name__,
                    'app_name': app_name,
                    'object_id': instance.id,
                }
                additional_info_adder(data, original_object=old_instance)
                logger.debug(data)
                EventLog.objects.create(**data)
    return track_field_changes


for app_name, model_details in settings.EVENT_LOGGER_TRACKED_FIELDS.items():
    for model_name, field_details in model_details.items():
        sender = '.'.join([app_name, model_name])
        signal_receiver = create_signal_receiever(sender, field_details, app_name=app_name)
        func_name = 'signal_receiver_{app_name}_{model_name}'.format(
            app_name=app_name, model_name=model_name)
        locals()[func_name] = signal_receiver
