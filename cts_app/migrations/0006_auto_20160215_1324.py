# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-15 10:24
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('cts_app', '0005_req'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='req',
            name='pub_date',
        ),
        migrations.AddField(
            model_name='req',
            name='apply time',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2016, 2, 15, 10, 24, 39, 407894, tzinfo=utc)),
            preserve_default=False,
        ),
    ]