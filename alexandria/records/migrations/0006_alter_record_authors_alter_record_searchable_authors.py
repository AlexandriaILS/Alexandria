# Generated by Django 4.0.2 on 2022-04-02 05:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("records", "0005_alter_subject_name"),
    ]

    operations = [
        migrations.AlterField(
            model_name="record",
            name="authors",
            field=models.CharField(blank=True, max_length=800, null=True),
        ),
        migrations.AlterField(
            model_name="record",
            name="searchable_authors",
            field=models.CharField(blank=True, max_length=800, null=True),
        ),
    ]
