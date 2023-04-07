# Generated by Django 4.1 on 2022-11-16 18:12

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("contenttypes", "0002_remove_content_type_name"),
    ]

    operations = [
        migrations.CreateModel(
            name="Bookmark",
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
                ("object_id", models.PositiveIntegerField()),
                (
                    "created_at",
                    models.DateTimeField(
                        db_index=True, default=django.utils.timezone.now
                    ),
                ),
                (
                    "content_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="contenttypes.contenttype",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="bookmarks",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Review",
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
                    "object_id",
                    models.PositiveIntegerField(
                        help_text="reviewed object ID", null=True
                    ),
                ),
                (
                    "target_id",
                    models.PositiveIntegerField(
                        blank=True, help_text="target object ID", null=True
                    ),
                ),
                (
                    "rating",
                    models.IntegerField(
                        choices=[(1, "1"), (2, "2"), (3, "3"), (4, "4"), (5, "5")],
                        default=0,
                    ),
                ),
                (
                    "message",
                    models.TextField(blank=True, null=True, verbose_name="message"),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        db_index=True, default=django.utils.timezone.now
                    ),
                ),
                (
                    "object_type",
                    models.ForeignKey(
                        help_text="reviewed object type",
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="review_objects",
                        to="contenttypes.contenttype",
                    ),
                ),
                (
                    "target_type",
                    models.ForeignKey(
                        blank=True,
                        help_text="target object type",
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="review_targets",
                        to="contenttypes.contenttype",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="ratings",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Review",
                "verbose_name_plural": "Reviews",
                "unique_together": {("user", "target_type", "id")},
            },
        ),
        migrations.CreateModel(
            name="Reaction",
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
                ("object_id", models.PositiveIntegerField()),
                (
                    "value",
                    models.CharField(
                        choices=[
                            ("like", "like"),
                            ("love", "love"),
                            ("pray", "pray"),
                            ("flap", "flap"),
                            ("funny", "funny"),
                            ("sad", "sad"),
                            ("angry", "angry"),
                        ],
                        default="like",
                        max_length=25,
                        verbose_name="value",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        db_index=True, default=django.utils.timezone.now
                    ),
                ),
                (
                    "content_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="contenttypes.contenttype",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reactions",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Reaction",
                "verbose_name_plural": "Reactions",
                "unique_together": {("user", "content_type", "id")},
            },
        ),
        migrations.CreateModel(
            name="Flag",
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
                ("object_id", models.PositiveIntegerField()),
                (
                    "value",
                    models.CharField(
                        choices=[
                            ("spam", "spam"),
                            ("sexual", "sexual"),
                            ("hate", "hate"),
                            ("violence", "violence"),
                            ("bullying", "bullying"),
                            ("hoax", "hoax"),
                            ("scam", "scam"),
                            ("illegal", "illegal"),
                            ("others", "others"),
                        ],
                        default="spam",
                        max_length=25,
                        verbose_name="value",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        db_index=True, default=django.utils.timezone.now
                    ),
                ),
                (
                    "message",
                    models.TextField(blank=True, null=True, verbose_name="message"),
                ),
                (
                    "content_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="contenttypes.contenttype",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="flags",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Flag",
                "verbose_name_plural": "Flags",
                "unique_together": {("user", "content_type", "id")},
            },
        ),
    ]