# Generated by Django 3.1.7 on 2021-03-23 13:06

import django.db.models.expressions
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_auto_20210322_2343'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='follow',
            name='follow_unique',
        ),
        migrations.AddConstraint(
            model_name='follow',
            constraint=models.CheckConstraint(check=models.Q(_negated=True, user=django.db.models.expressions.F('author')), name='Обнаружена самоподписка'),
        ),
        migrations.AddConstraint(
            model_name='follow',
            constraint=models.UniqueConstraint(fields=('user', 'author'), name='follow_unique'),
        ),
    ]