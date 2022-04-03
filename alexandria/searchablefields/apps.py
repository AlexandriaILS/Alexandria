from django.apps import AppConfig, apps
from django.db import models as django_models


class SearchableFieldsException(Exception):
    pass


class SearchablefieldsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "alexandria.searchablefields"

    def ready(self) -> None:
        """
        So let's talk about searching for a moment. When we're using the search
        bar to take in text, the problem is that the text that we take in isn't
        always representative of the text that we want to find. Therefore, we
        need to convert it somehow into something that we _can_ find. For example,
        a book title that has an apostrophe in it won't be findable easily when
        we search for it if we omit the apostrophe; the same goes for unicode
        characters with fancy additions, like umlauts and the like.

        The best way to handle this is to maintain a secondary field of the cleaned
        value so that we can query it through the DB, but then we run into a
        second problem; maintainability. It's another thing to remember to update,
        another thing to copy and paste, and another place that things can fall
        through the cracks. So what we do here is bypass... all of that.

        All you need to do is add a list of strings called `SEARCHABLE_FIELDS` to
        the top level of the model. When that's done, then it will automatically
        be picked up and will have all the extra fields created (or updated to
        match the original) silently in the background. This type of operation
        is generally considered to be A Bad Idea(tm), but in terms of
        maintainability, I think that we manage to save ourselves some long-term
        pain by setting this up.
        """

        models = apps.get_models()
        models = [m for m in models if hasattr(m, "SEARCHABLE_FIELDS")]

        for model in models:
            target_fields = model.SEARCHABLE_FIELDS
            if not target_fields:
                # maybe the field is there but it's empty?
                continue

            for field in target_fields:
                # First, verify that the field actually exists and that it's something
                # that we can work on
                if original_field := getattr(model, field, None):
                    field_base = original_field.field
                    if not isinstance(field_base, django_models.CharField):
                        raise SearchableFieldsException(
                            "Can only create searchable versions of CharFields."
                        )
                else:
                    # Maybe a spelling error? Either way, we don't see the original
                    # field.
                    raise SearchableFieldsException(
                        f"Cannot find requested field {field}"
                    )

                new_field_name = f"searchable_{field.lower()}"
                if not hasattr(model, new_field_name):
                    options = {
                        name: getattr(field_base, name)
                        for name in ["null", "blank", "max_length"]
                        if hasattr(field_base, name)
                    }
                    field_base.__class__(**options, db_index=True).contribute_to_class(
                        model, new_field_name
                    )
