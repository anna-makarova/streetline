# Generated by Django 3.2.5 on 2022-11-13 17:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('route', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='segment',
            name='mean_score',
            field=models.FloatField(default=3),
        ),
    ]
