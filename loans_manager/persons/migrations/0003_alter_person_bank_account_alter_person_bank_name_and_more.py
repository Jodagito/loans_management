# Generated by Django 5.1.3 on 2024-12-03 23:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('persons', '0002_remove_person_loans_person_loans'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='bank_account',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='person',
            name='bank_name',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='person',
            name='phone',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
