# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-03-24 10:41
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('cts_app', '0010_votes'),
    ]

    operations = [
        migrations.AddField(
            model_name='votes',
            name='pub_date',
            field=models.DateTimeField(auto_now=True, default=datetime.datetime(2016, 3, 24, 10, 41, 58, 196931, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
