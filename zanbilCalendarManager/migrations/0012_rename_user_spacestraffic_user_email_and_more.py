# Generated by Django 4.0 on 2022-02-12 20:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('zanbilCalendarManager', '0011_spacestraffic'),
    ]

    operations = [
        migrations.RenameField(
            model_name='spacestraffic',
            old_name='user',
            new_name='user_email',
        ),
        migrations.AlterField(
            model_name='spacestraffic',
            name='checkin_datetime',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Checkin date & time'),
        ),
    ]
