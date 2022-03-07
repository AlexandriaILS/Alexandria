from rest_framework import serializers

from alexandria.records.models import Hold, Item, Record


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = [
            "id",
            "barcode",
            "record",
            "is_available",
            "price",
            "condition",
            "home_location",
            "is_active",
            "isbn",
            "issn",
            "call_number",
            "can_circulate",
            "publisher",
            "pubyear",
            "edition",
            "type",
        ]


class HoldSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hold
        fields = [
            "date_created",
            "placed_for",
            "notes",
            "destination",
            "item",
            "specific_copy",
            "force_next_available",
        ]


class RecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Record
        fields = [
            "id",
            "authors",
            "subtitle",
            "uniform_title",
            "notes",
            "series",
            "subjects",
            "tags",
            "type",
            "bibliographic_level",
            "summary",
            "zenodotus_id",
            "zenodotus_record_version",
        ]
