# Generated by Django 4.0 on 2022-04-28 10:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('zanbilCalendarManager', '0026_spacestraffic_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='spacestraffic',
            name='event',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='zanbilCalendarManager.event'),
        ),
    ]