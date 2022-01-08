from alexandria.searchablefields.strings import clean_text


class SearchableFieldMixin:
    def get_searchable_field_names(self) -> list:
        return ["searchable_" + name for name in self.SEARCHABLE_FIELDS]

    def get_searchable_field_map(self) -> dict:
        return {name: "searchable_" + name for name in self.SEARCHABLE_FIELDS}

    def convert_to_searchable(self, text: str) -> str:
        return clean_text(text)

    def update_searchable_fields(self) -> None:
        field_map = self.get_searchable_field_map()
        for original, searchable in field_map.items():
            setattr(
                self, searchable, self.convert_to_searchable(getattr(self, original))
            )
