# Generated by Django 3.1.5 on 2021-03-07 06:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('holds', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='hold',
            name='pull_any_same_type',
            field=models.BooleanField(default=True),
        ),
    ]