# Generated by Django 3.0.3 on 2020-03-24 18:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('larps', '0003_auto_20200324_1840'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bookings',
            name='weapon',
            field=models.BooleanField(blank=True, null=True),
        ),
    ]