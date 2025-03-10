# Generated by Django 5.1.3 on 2024-12-03 23:17

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('due_date', models.DateField()),
                ('payment_method', models.CharField(choices=[('cash', 'Cash'), ('debit', 'Debit')], max_length=5)),
            ],
        ),
    ]
