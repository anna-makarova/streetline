# Generated by Django 3.2.5 on 2022-11-14 11:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('route', '0002_segment_mean_score'),
    ]

    operations = [
        migrations.AlterField(
            model_name='segment',
            name='mean_score',
            field=models.IntegerField(default=3),
        ),
    ]
