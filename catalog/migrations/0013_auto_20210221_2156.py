# Generated by Django 3.1.5 on 2021-02-21 21:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0012_item_edition"),
    ]

    operations = [
        migrations.AddField(
            model_name="record",
            name="zenodotus_id",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="record",
            name="zenodotus_record_version",
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
