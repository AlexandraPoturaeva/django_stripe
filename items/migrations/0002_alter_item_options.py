# Generated by Django 4.2.7 on 2023-11-30 06:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='item',
            options={'get_latest_by': 'created_at', 'ordering': ['-created_at', 'name']},
        ),
    ]