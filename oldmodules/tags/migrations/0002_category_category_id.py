# Generated by Django 4.0.7 on 2023-03-28 02:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coreplus_tags', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='category_id',
            field=models.CharField(blank=True, max_length=80, null=True, unique=True, verbose_name='Category ID'),
        ),
    ]