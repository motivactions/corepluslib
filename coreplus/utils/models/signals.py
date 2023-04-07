from django.db.models.signals import ModelSignal

pre_trash = ModelSignal(use_caching=True)
post_trash = ModelSignal(use_caching=True)

pre_validate = ModelSignal(use_caching=True)
post_validate = ModelSignal(use_caching=True)

pre_cancel = ModelSignal(use_caching=True)
post_cancel = ModelSignal(use_caching=True)

pre_approve = ModelSignal(use_caching=True)
post_approve = ModelSignal(use_caching=True)

pre_confirm = ModelSignal(use_caching=True)
post_confirm = ModelSignal(use_caching=True)

pre_reject = ModelSignal(use_caching=True)
post_reject = ModelSignal(use_caching=True)

pre_complete = ModelSignal(use_caching=True)
post_complete = ModelSignal(use_caching=True)

pre_process = ModelSignal(use_caching=True)
post_process = ModelSignal(use_caching=True)

pre_invoicing = ModelSignal(use_caching=True)
post_invoicing = ModelSignal(use_caching=True)

pre_pay = ModelSignal(use_caching=True)
post_pay = ModelSignal(use_caching=True)

pre_close = ModelSignal(use_caching=True)
post_close = ModelSignal(use_caching=True)

pre_archive = ModelSignal(use_caching=True)
post_archive = ModelSignal(use_caching=True)
