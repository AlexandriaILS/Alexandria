# Generated by Django 3.1.5 on 2021-06-26 18:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_auto_20210626_1827'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alexandriauser',
            name='card_number',
            field=models.CharField(max_length=50, primary_key=True, serialize=False),
        ),
    ]
