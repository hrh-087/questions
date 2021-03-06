# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-05-13 03:51
from __future__ import unicode_literals

from django.db import migrations
import easy_thumbnails.fields


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='avator_sm',
        ),
        migrations.AlterField(
            model_name='user',
            name='avator_sor',
            field=easy_thumbnails.fields.ThumbnailerImageField(default='avator/default.jpg', upload_to='avator/%Y%m%d/', verbose_name='头像'),
        ),
    ]
