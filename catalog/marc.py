from typing import Union

import pymarc
from django.conf import settings
from django.db.models import QuerySet

from catalog.models import Item, Record, Subject
from users.models import BranchLocation


def get_marc_subfield_from_field(
    field: pymarc.Field, identifier: str
) -> Union[str, None]:
    """Retrieve a specific subfield value, like `a` or `b`, from a field."""
    # get_subfields doesn't always work, so we'll just fish manually for them.
    # It'll be in a list that looks like this: ['a', 'a_value', 'b', 'b_value'...]
    for field_id in range(0, len(field.subfields), 2):
        if field.subfields[field_id] == identifier:
            return field.subfields[field_id + 1]
    return None


def get_subjects(marc_record):
    qs = QuerySet()
    for marc_subject in marc_record.subjects():
        subject_obj, _ = Subject.objects.get_or_create(
            name__iexact=marc_subject.value()
        )
        qs = qs | QuerySet(subject_obj)
    return qs


def import_from_marc(marc_record: pymarc.Record) -> Item:
    if (author_str := get_marc_subfield_from_field(marc_record["245"], "c")) is None:
        # want to pull the author string from 245c because that field includes all
        # authors; the canonical author field only includes the first author.
        author_str = marc_record.author()

    title = get_marc_subfield_from_field(marc_record["245"], "a")
    subtitle = get_marc_subfield_from_field(marc_record["245"], "b")

    base_record = Record(
        title=title,
        subtitle=subtitle,
        authors=author_str,
        uniform_title=marc_record.uniformtitle(),
        notes=marc_record.notes(),
        series=marc_record.series(),
    )
    # generate an ID so that we can use it in the next step
    base_record.save()

    base_record.subjects.add(*get_subjects(marc_record))
    base_record.save()

    return Item.objects.create(
        record=base_record,
        publisher=marc_record.publisher(),
        barcode=1234,
        marc_leader=marc_record.leader,
        home_location=(
            None
            if settings.FLOATING_COLLECTION
            else BranchLocation.objects.get(id=settings.DEFAULT_LOCATION_ID)
        ),
        isbn=marc_record.isbn(),
        issn=marc_record.issn(),
        issn_title=marc_record.issn_title(),
        marc_location=marc_record.location(),
        call_number=marc_record["050"].value(),
        sudoc=marc_record.sudoc(),
        physical_description=marc_record.physicaldescription(),
        pubyear=marc_record.pubyear(),
    )
