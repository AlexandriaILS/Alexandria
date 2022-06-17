# Generated by Django 4.0.4 on 2022-05-30 03:16

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        ("records", "0006_alter_checkoutsession_object_id_alter_item_object_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="checkoutsession",
            name="content_type",
            field=models.ForeignKey(
                blank=True,
                limit_choices_to={"model__in": ("branchlocation", "user")},
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="contenttypes.contenttype",
            ),
        ),
        migrations.AlterField(
            model_name="item",
            name="content_type",
            field=models.ForeignKey(
                blank=True,
                limit_choices_to={"model__in": ("branchlocation", "user")},
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="contenttypes.contenttype",
            ),
        ),
    ]
