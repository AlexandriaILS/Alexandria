from django.db import migrations
from django.contrib.postgres.operations import TrigramExtension


class Migration(migrations.Migration):

    dependencies = [
        ("records", "0006_alter_record_authors_alter_record_searchable_authors"),
    ]

    operations = [TrigramExtension()]
