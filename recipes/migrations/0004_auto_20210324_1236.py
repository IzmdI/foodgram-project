# Generated by Django 3.1.7 on 2021-03-24 09:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_auto_20210323_1606'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recipe',
            name='favorites',
        ),
        migrations.RemoveField(
            model_name='recipe',
            name='purchases',
        ),
    ]
