# Generated by Django 4.2.7 on 2023-12-02 10:15

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0003_itemsinorder_order_itemsinorder_order'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tax',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('display_name', models.CharField(max_length=10)),
                ('inclusive', models.BooleanField()),
                ('percentage', models.DecimalField(decimal_places=4, max_digits=7, validators=[django.core.validators.MinValueValidator(0)])),
                ('country', models.CharField(blank=True, max_length=2, null=True)),
                ('state', models.CharField(blank=True, max_length=50, null=True)),
                ('jurisdiction', models.CharField(blank=True, max_length=100, null=True)),
                ('description', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
