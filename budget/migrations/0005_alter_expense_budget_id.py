# Generated by Django 5.1 on 2024-09-17 00:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('budget', '0004_alter_expense_budget_id_alter_expense_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expense',
            name='budget_id',
            field=models.IntegerField(choices=[(1, '1-2024'), (10, '10-2024'), (11, '11-2024'), (12, '12-2024'), (2, '2-2024'), (3, '3-2024'), (4, '4-2024'), (5, '5-2024'), (6, '6-2024'), (7, '7-2024'), (8, '8-2024'), (9, '9-2024')], default=9),
        ),
    ]
