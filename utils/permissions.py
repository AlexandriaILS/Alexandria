# coding=utf-8
"""
The MIT License (MIT)

Copyright (c) 2015 Alisue, hashnote.net

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

Originally retrieved from
https://github.com/lambdalisue/django-permission/blob/master/src/permission/utils/permissions.py
on 2021/11/28.

Modifications by @itsthejoker.

Permission utility module.

In this module, term *perm* indicate the identifier string permission written
in 'app_label.codename' format.
"""
from __future__ import unicode_literals
from functools import wraps


def permission_or_none(perm):
    """
    Decorator for views that checks whether a user has a particular permission
    enabled and returns None if they don't.
    This is pretty much just the code for the `permission_required` decorator and
    `user_passes_test` mashed together.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if isinstance(perm, str):
                perms = (perm,)
            else:
                perms = perm
            # First check if the user has the permission (even anon users)
            if request.user.has_perms(perms):
                return view_func(request, *args, **kwargs)
            return None
        return _wrapped_view
    return decorator


def get_perm_codename(perm, fail_silently=True):
    """
    Get permission codename from permission-string.

    Examples
    --------
    >>> get_perm_codename('app_label.codename_model')
    'codename_model'
    >>> get_perm_codename('app_label.codename')
    'codename'
    >>> get_perm_codename('codename_model')
    'codename_model'
    >>> get_perm_codename('codename')
    'codename'
    >>> get_perm_codename('app_label.app_label.codename_model')
    'app_label.codename_model'
    """
    try:
        perm = perm.split(".", 1)[1]
    except IndexError as e:
        if not fail_silently:
            raise e
    return perm


def permission_to_perm(permission):
    """
    Convert a permission instance to a permission-string.

    Examples
    --------
    >>> permission = Permission.objects.get(
    ...     content_type__app_label='auth',
    ...     codename='add_user',
    ... )
    >>> permission_to_perm(permission)
    'auth.add_user'
    """
    app_label = permission.content_type.app_label
    codename = permission.codename
    return "%s.%s" % (app_label, codename)


def perm_to_permission(perm):
    """
    Convert a permission-string to a permission instance.

    Examples
    --------
    >>> permission = perm_to_permission('auth.add_user')
    >>> permission.content_type.app_label
    'auth'
    >>> permission.codename
    'add_user'
    """
    from django.contrib.auth.models import Permission

    try:
        app_label, codename = perm.split(".", 1)
    except (ValueError, IndexError):
        raise AttributeError(
            "The format of identifier string permission (perm) is wrong. "
            "It should be in 'app_label.codename'."
        )
    else:
        permission = Permission.objects.get(
            content_type__app_label=app_label, codename=codename
        )
        return permission


def get_app_perms(model_or_app_label):
    """
    Get permission-string list of the specified django application.

    Parameters
    ----------
    model_or_app_label : model class or string
        A model class or app_label string to specify the particular django
        application.

    Returns
    -------
    set
        A set of perms of the specified django application.

    Examples
    --------
    >>> perms1 = get_app_perms('auth')
    >>> perms2 = get_app_perms(Permission)
    >>> perms1 == perms2
    True
    """
    from django.contrib.auth.models import Permission

    if isinstance(model_or_app_label, str):
        app_label = model_or_app_label
    else:
        # assume model_or_app_label is model class
        app_label = model_or_app_label._meta.app_label
    qs = Permission.objects.filter(content_type__app_label=app_label)
    perms = ("%s.%s" % (app_label, p.codename) for p in qs.iterator())
    return set(perms)


def get_model_perms(model):
    """
    Get permission-string list of a specified django model.

    Parameters
    ----------
    model : model class
        A model class to specify the particular django model.

    Returns
    -------
    set
        A set of perms of the specified django model.

    Examples
    --------
    >>> sorted(get_model_perms(Permission)) == [
    ...     'auth.add_permission',
    ...     'auth.change_permission',
    ...     'auth.delete_permission'
    ... ]
    True
    """
    from django.contrib.auth.models import Permission

    app_label = model._meta.app_label
    model_name = model._meta.object_name.lower()
    qs = Permission.objects.filter(
        content_type__app_label=app_label, content_type__model=model_name
    )
    perms = ("%s.%s" % (app_label, p.codename) for p in qs.iterator())
    return set(perms)
