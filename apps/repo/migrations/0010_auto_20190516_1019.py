# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-05-16 02:19
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('repo', '0009_auto_20190515_1110'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='questions',
            options={'permissions': (('can_change_question_status', '可以修改题目状态'),), 'verbose_name': '题库', 'verbose_name_plural': '题库'},
        ),
    ]