# Generated by Django 4.0 on 2022-01-20 01:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('zanbilCalendarManager', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chair',
            name='chair_name',
            field=models.CharField(max_length=50, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='office',
            name='office_name',
            field=models.CharField(max_length=50, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='room',
            name='room_name',
            field=models.CharField(max_length=50, verbose_name='Name'),
        ),
    ]
