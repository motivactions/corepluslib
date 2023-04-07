from django.apps import apps


def get_polymorpohic_choice(models, key_name=None, separator=None, sort_value=False):
    def format_key(ct, sep):
        """return id.app_lable.model_name"""
        if not sep:
            sep = "__"
        if key_name in [None, "id"]:
            return getattr(ct, "id")
        elif len(key_name) == 1:
            return getattr(ct, key_name)
        else:
            return sep.join([str(getattr(ct, field)) for field in key_name])

    contenttype = apps.get_model("contenttypes", "ContentType")
    ct_map = contenttype.objects.get_for_models(*models)
    ct_list = [
        (format_key(ct, separator), model._meta.verbose_name.title())
        for model, ct in ct_map.items()
    ]
    if sort_value:
        sorted(ct_list, key=lambda x: x[1])
    else:
        return ct_list
