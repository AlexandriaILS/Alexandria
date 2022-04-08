# Generated by Django 4.0.1 on 2022-01-11 04:30

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("users", "0001_initial"),
        ("records", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="item",
            name="home_location",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="users.branchlocation",
            ),
        ),
        migrations.AddField(
            model_name="item",
            name="record",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="records.record"
            ),
        ),
        migrations.AddField(
            model_name="item",
            name="type",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="records.itemtype",
            ),
        ),
        migrations.AddField(
            model_name="hold",
            name="destination",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="users.branchlocation",
            ),
        ),
        migrations.AddField(
            model_name="hold",
            name="item",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="records.item",
            ),
        ),
        migrations.AddField(
            model_name="hold",
            name="placed_by",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddField(
            model_name="collection",
            name="home",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="users.branchlocation",
            ),
        ),
    ]
