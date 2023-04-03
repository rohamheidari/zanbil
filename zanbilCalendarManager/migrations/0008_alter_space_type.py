# Generated by Django 4.0 on 2022-01-24 01:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('zanbilCalendarManager', '0007_alter_space_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='space',
            name='type',
            field=models.CharField(choices=[('c', 'Chair'), ('r', 'Room')], default='r', max_length=1),
        ),
    ]