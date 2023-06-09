# Generated by Django 4.0 on 2022-02-20 19:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('zanbilCalendarManager', '0014_event_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='creator',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='auth.user'),
        ),
        migrations.AddField(
            model_name='event',
            name='status',
            field=models.CharField(choices=[('p', 'Pending'), ('b', 'Busy')], default='p', max_length=1),
        ),
    ]
