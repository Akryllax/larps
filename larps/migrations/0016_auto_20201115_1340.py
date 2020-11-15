# Generated by Django 3.1.3 on 2020-11-15 12:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('larps', '0015_auto_20201110_2147'),
    ]

    operations = [
        migrations.AddField(
            model_name='accomodation',
            name='larp',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='larps.larp'),
        ),
        migrations.AddField(
            model_name='busstop',
            name='larp',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='larps.larp'),
        ),
    ]