# Generated by Django 4.0 on 2022-04-28 10:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('zanbilCalendarManager', '0025_accessrequest'),
    ]

    operations = [
        migrations.AddField(
            model_name='spacestraffic',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='auth.user'),
        ),
    ]