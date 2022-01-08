from django.db import connection, reset_queries
import time
import functools

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
