# Generated by Django 3.1.5 on 2021-02-27 20:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0013_auto_20210221_2156"),
    ]

    operations = [
        migrations.AddField(
            model_name="record",
            name="summary",
            field=models.TextField(blank=True, null=True),
        ),
    ]
