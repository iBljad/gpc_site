# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-22 12:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cts_app', '0007_auto_20160215_1326'),
    ]

    operations = [
        migrations.AlterField(
            model_name='req',
            name='comment',
            field=models.CharField(max_length=280),
        ),
        migrations.AlterField(
            model_name='req',
            name='nickname',
            field=models.CharField(max_length=20),
        ),
    ]