from django.contrib.postgres.operations import TrigramExtension
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("records", "0006_alter_record_authors_alter_record_searchable_authors"),
    ]

    operations = [TrigramExtension()]
