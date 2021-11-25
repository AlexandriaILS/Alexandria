from django.db import connection, reset_queries
import time
import functools

from utils.strings import clean_text


def filter_db(request, klass, *args, **kwargs):
    """Filter the requested class and enforce the host check."""
    kwargs["host"] = request.host
    return klass.objects.filter(*args, **kwargs)


def query_debugger(func):
    # https://betterprogramming.pub/django-select-related-and-prefetch-related-f23043fd635d
    @functools.wraps(func)
    def inner_func(*args, **kwargs):
        reset_queries()

        start_queries = len(connection.queries)

        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()

        end_queries = len(connection.queries)

        print(f"Function: {func.__name__}")
        print(f"Number of Queries: {end_queries - start_queries}")
        print(f"Finished in: {(end - start):.2f}s")
        return result

    return inner_func


class SearchableHelpers:

    def get_searchable_field_names(self) -> list:
        return ["searchable_"+name for name in self.SEARCHABLE_FIELDS]

    def get_searchable_field_map(self) -> dict:
        return {name: "searchable_"+name for name in self.SEARCHABLE_FIELDS}

    def convert_to_searchable(self, text: str) -> str:
        return clean_text(text)

    def update_searchable_fields(self) -> None:
        field_map = self.get_searchable_field_map()
        for original, searchable in field_map.items():
            setattr(self, searchable, self.convert_to_searchable(getattr(self, original)))
