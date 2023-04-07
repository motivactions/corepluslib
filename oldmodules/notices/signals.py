""" Django notifications signal file """
# -*- coding: utf-8 -*-
from django.dispatch import Signal

bulk_notify = Signal()
firebase_push_notify = Signal()
apns_push_notify = Signal()
web_push_notify = Signal()
