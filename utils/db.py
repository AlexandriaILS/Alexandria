def filter(request, klass, *args, **kwargs):
    """Filter the requested class and enforce the host check."""
    kwargs['host'] = request.host
    return klass.objects.filter(*args, **kwargs)
