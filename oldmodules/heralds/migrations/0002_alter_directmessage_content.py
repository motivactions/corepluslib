# Generated by Django 4.0.7 on 2023-01-31 03:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coreplus_heralds', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='directmessage',
            name='content',
            field=models.TextField(blank=True, max_length=1000, null=True, verbose_name='Content'),
        ),
    ]