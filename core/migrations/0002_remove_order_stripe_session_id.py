# Generated by Django 4.0 on 2022-01-09 05:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='stripe_session_id',
        ),
    ]
