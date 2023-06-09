# Generated by Django 4.1 on 2022-11-16 18:12

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("sites", "0002_alter_domain_unique"),
    ]

    operations = [
        migrations.CreateModel(
            name="GeneralSetting",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "site_logo",
                    models.ImageField(
                        blank=True, null=True, upload_to="", verbose_name="Logo"
                    ),
                ),
                (
                    "site_name",
                    models.CharField(
                        blank=True, max_length=255, null=True, verbose_name="Site Name"
                    ),
                ),
                (
                    "site_description",
                    models.TextField(blank=True, null=True, verbose_name="Site Name"),
                ),
                (
                    "site",
                    models.OneToOneField(
                        editable=False,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="sites.site",
                    ),
                ),
            ],
            options={
                "verbose_name": "General Setting",
                "verbose_name_plural": "General Settings",
            },
        ),
    ]
