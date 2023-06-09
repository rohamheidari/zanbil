# Generated by Django 4.0 on 2022-02-12 20:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('zanbilCalendarManager', '0010_rename_upload_space_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='SpacesTraffic',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.EmailField(max_length=254, verbose_name='Email')),
                ('event_gid', models.CharField(max_length=100, verbose_name='google calendar id')),
                ('checkin_datetime', models.DateTimeField(verbose_name='Checkin date & time')),
                ('checkout_datetime', models.DateTimeField(blank=True, null=True, verbose_name='Checkin date & time')),
                ('space', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='zanbilCalendarManager.space')),
            ],
        ),
    ]
