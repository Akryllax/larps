# Generated by Django 3.1.3 on 2020-11-19 19:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('larps', '0017_player_sleeve_length'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bookings',
            name='weapon',
        ),
    ]
