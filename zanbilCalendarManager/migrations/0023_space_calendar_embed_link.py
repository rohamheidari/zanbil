# Generated by Django 4.0 on 2022-04-18 09:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('zanbilCalendarManager', '0022_alter_event_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='space',
            name='calendar_embed_link',
            field=models.CharField(default=None, max_length=2000, null=True),
            preserve_default=False,
        ),
    ]