# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-05-16 07:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_auto_20190516_1449'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.CharField(max_length=32, unique=True, verbose_name='邮箱'),
        ),
    ]