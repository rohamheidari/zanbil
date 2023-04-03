# Generated by Django 4.0 on 2022-01-24 00:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('zanbilCalendarManager', '0005_alter_chair_upload_alter_office_location_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Space',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Name')),
                ('calendar_id', models.CharField(max_length=100)),
                ('type', models.CharField(choices=[('c', 'Chair'), ('r', 'Room')], default='r', max_length=1)),
                ('capacity', models.IntegerField(blank=True, null=True)),
                ('upload', models.ImageField(blank=True, null=True, upload_to='covers/%Y/%m/%d/')),
                ('office', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='zanbilCalendarManager.office')),
            ],
        ),
        migrations.DeleteModel(
            name='Room',
        ),
    ]