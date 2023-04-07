from django.apps import apps
from django_rq import job

from .signals import bulk_notify

get_model = apps.get_model


@job
def create_notification_job():
    bulk_notify.send()


@job
def send_email_notification_job():
    pass


@job
def send_push_notification_job(obj_id, app_label, model_name, recipients=None):
    pass
