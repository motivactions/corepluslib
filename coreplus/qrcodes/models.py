import hashlib
import io
import uuid
from pathlib import Path

import qrcode
from django.conf import settings
from django.core.files import File
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from PIL import Image

DEFAULT_LOGO = Path(__file__).parent / "static" / "qrcodes" / "img" / "qr_logo.png"

QR_LOGO = getattr(settings, "QR_LOGO", None)


class QRCodeMixin(models.Model):

    qr_version = 1
    qr_box_size = 10
    qr_border = 2
    qr_format = "png"
    qr_uid_field = "qruid"
    qr_color = None
    qr_width = 100
    qr_error_correction = qrcode.constants.ERROR_CORRECT_L
    qruid = models.CharField(
        max_length=8,
        verbose_name=_("UID"),
        editable=False,
        null=True,
        blank=False,
    )
    qr_image = models.ImageField(
        upload_to="qrcode",
        blank=True,
        null=True,
        # editable=False,
    )
    qr_data = models.CharField(
        "qr data",
        default="",
        null=True,
        editable=False,
        max_length=500,
        help_text="Track qrcode data field",
    )

    _old_data = ""

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._qrcode_data = self.qr_data

    @cached_property
    def opts(self):
        return self.__class__._meta

    def get_qr_format(self):
        return self.qr_format

    def get_qr_data(self):
        raise NotImplementedError(
            "%s must implement get_qr_data()." % self.__class__.__name__
        )

    def make_qr_filename(self):
        code = self.make_qr_uid()
        qr_format = self.get_qr_format()
        return "%s_%s_%s.%s" % (
            self.opts.app_label,
            self.opts.model_name,
            code,
            qr_format,
        )

    def make_qr_logo(self, qr_image):
        Logo_link_path = QR_LOGO
        logo = Image.open(Logo_link_path)
        logo = logo.convert("RGBA")
        wpercent = self.qr_width / float(logo.size[0])
        hsize = int((float(logo.size[1]) * float(wpercent)))
        logo = logo.resize((self.qr_width, hsize), Image.ANTIALIAS)
        # set size of QR code
        pos = (
            (qr_image.size[0] - logo.size[0]) // 2,
            (qr_image.size[1] - logo.size[1]) // 2,
        )
        qr_image.paste(logo, pos, logo)
        return qr_image

    def make_qr_image(self):
        qr = qrcode.QRCode(
            version=self.qr_version,
            error_correction=self.qr_error_correction,
            box_size=self.qr_box_size,
            border=self.qr_border,
        )
        qr.add_data(self.get_qr_data())
        qr_image = qr.make_image().convert("RGB")
        # if using_logo
        if QR_LOGO is not None:
            try:
                qr_image = self.make_qr_logo(qr_image)
            except Exception as err:
                print(err)
        return qr_image

    def make_qr_uid(self, uid_field="qruid", max_len=8):
        code = str(uuid.uuid4())[:8]
        # Ensure code does not aleady exist
        try:
            kwargs = {uid_field: code}
            self.__class__.objects.get(**kwargs)
        except self.__class__.DoesNotExist:
            return code
        return self.make_qr_uid(uid_field, max_len)

    def make_qrcode(self):
        stream = io.BytesIO()
        self.make_qr_image().save(stream, format=self.get_qr_format())
        self.qr_image.save(self.make_qr_filename(), File(stream), save=False)
        stream.close()

    def _data_changed(self):
        old = hashlib.md5(str(self._qrcode_data).encode("utf-8")).digest()
        new = hashlib.md5(str(self.qr_data).encode("utf-8")).digest()
        return new != old

    def save(self, *args, **kwargs):
        if self._data_changed():
            if bool(self.qr_image):
                self.qr_image.delete(save=False)
        self.make_qrcode()
        super().save(*args, **kwargs)

    def delete(self, using=None, keep_parents=False):
        if bool(self.qr_image):
            self.qr_image.delete(save=False)
        super().delete(using=using, keep_parents=keep_parents)
