import re
from typing import List, Union

import pymarc
from django.conf import settings

from alexandria.records.models import Item, Record, Subject, BibliographicLevel
from alexandria.users.models import BranchLocation

YEAR_RE = r"[0-9]{4}"


def get_marc_subfield_from_field(
    field: pymarc.Field, identifier: str
) -> Union[str, None]:
    """Retrieve a specific subfield value, like `a` or `b`, from a field."""
    # get_subfields doesn't always work, so we'll just fish manually for them.
    # It'll be in a list that looks like this: ['a', 'a_value', 'b', 'b_value'...]
    if not field:
        return
    for field_id in range(0, len(field.subfields), 2):
        if field.subfields[field_id] == identifier:
            return field.subfields[field_id + 1]
    return None


def get_subjects(marc_record: pymarc.Record) -> List:
    subject_list = []
    for marc_subject in marc_record.subjects():
        subject_obj, _ = Subject.objects.get_or_create(name=marc_subject.value())
        subject_list.append(subject_obj)
    return subject_list


def import_from_marc(marc_record: pymarc.Record) -> Item:
    if (author_str := get_marc_subfield_from_field(marc_record["245"], "c")) is None:
        # want to pull the author string from 245c because that field includes all
        # authors; the canonical author field only includes the first author.
        author_str = marc_record.author()

    title = get_marc_subfield_from_field(marc_record["245"], "a")
    subtitle = get_marc_subfield_from_field(marc_record["245"], "b")
    notes = "\n".join([f"{n.tag}: {n.value()}" for n in marc_record.notes()])
    summary = get_marc_subfield_from_field(marc_record["520"], "a")

    series = (
        None
        if marc_record.series() == []
        else "\n".join([series.value() for series in marc_record.series()])
    )

    base_record = Record(
        title=title,
        subtitle=subtitle,
        authors=author_str,
        uniform_title=marc_record.uniformtitle(),
        notes=notes,
        series=series,
        summary=summary,
    )
    # generate an ID so that we can use it in the next step
    base_record.save()

    base_record.subjects.add(*get_subjects(marc_record))
    base_record.save()

    pubyear = re.search(YEAR_RE, marc_record.pubyear())
    if pubyear:
        pubyear = pubyear.group()

    physical_description = marc_record.physicaldescription()
    if len(physical_description) > 0:
        physical_description = physical_description[0].value()

    bibliographic_level, _ = BibliographicLevel.objects.get_or_create(
        name=pymarc.Leader(marc_record.leader).bibliographic_level
    )

    location = None if marc_record.location() == [] else marc_record.location()

    return Item.objects.create(
        record=base_record,
        publisher=marc_record.publisher(),
        barcode=0,
        marc_leader=marc_record.leader,
        home_location=(
            None
            if settings.FLOATING_COLLECTION
            else BranchLocation.objects.get(id=settings.DEFAULT_LOCATION_ID)
        ),
        isbn=marc_record.isbn(),
        issn=marc_record.issn(),
        issn_title=marc_record.issn_title(),
        marc_location=location,
        call_number=marc_record["050"].value(),
        sudoc=marc_record.sudoc(),
        physical_description=physical_description,
        pubyear=pubyear,
        bibliographic_level=bibliographic_level,
    )
