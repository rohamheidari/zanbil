# Generated by Django 4.0 on 2022-04-28 10:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('zanbilCalendarManager', '0027_spacestraffic_event'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='spacestraffic',
            name='event_gid',
        ),
        migrations.RemoveField(
            model_name='spacestraffic',
            name='space',
        ),
        migrations.RemoveField(
            model_name='spacestraffic',
            name='user_email',
        ),
    ]
