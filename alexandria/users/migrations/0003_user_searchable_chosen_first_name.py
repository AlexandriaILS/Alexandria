# Generated by Django 4.0.4 on 2022-05-29 00:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0002_user_chosen_first_name"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="searchable_chosen_first_name",
            field=models.CharField(
                blank=True, db_index=True, max_length=255, null=True
            ),
        ),
    ]
