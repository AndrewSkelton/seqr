# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-07-26 13:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0030_auto_20170621_1446'),
    ]

    operations = [
        migrations.AlterField(
            model_name='family',
            name='short_description',
            field=models.CharField(blank=True, default=b'', max_length=500),
        ),
    ]
