from typing import Dict

from django.conf import settings

import requests


def slash_join(*args: str, params: Dict = None) -> str:
    # urljoin is too limited for the urls that I want to construct, so here's
    # a helper function for it.
    # Original inspiration from https://codereview.stackexchange.com/a/175423
    result = "/".join(arg.strip("/") for arg in args) + "/"
    if params:
        params = f"?" + "&".join(
            [
                *list(
                    [
                        f"{key}={params[key]}"
                        for key in params.keys()
                        if params[key] != None
                    ]
                )
            ]
        )
        result += params
    return result


def get_base_id(route, level) -> [int, None]:
    resp = requests.get(slash_join(settings.ZENODOTUS_URL, "api", route))
    resp.raise_for_status()
    for item in resp.json():
        if item["name"] == level.get_name_display():
            return item["id"]
    return None


def sync_object_with_z(object, endpoint, itemtype=False) -> int:
    # Check to make sure that a string string isn't already with Z; if it
    # is, then return the ID number. Otherwise, create the subject and return
    # the ID.
    resp = requests.get(
        slash_join(settings.ZENODOTUS_URL, "api", endpoint, params={"q": object.name})
    )
    resp.raise_for_status()
    result = resp.json()
    if len(result) > 0:
        return result[0].get("id")
    else:
        data = {"name": object.name}
        if itemtype:
            data.update({"base": get_base_id("itemtypebase", object.base)})

        resp = requests.post(
            slash_join(settings.ZENODOTUS_URL, "api", endpoint), data=data
        )
        resp.raise_for_status()
        return resp.json().get("id")


def upload(record):

    if not record.zenodotus_id:
        # Either this was not pulled from Z or it hasn't been linked to a Z
        # record. Let's first see if the record (or something that we think
        # is the record) already exists.
        new_url = slash_join(settings.ZENODOTUS_URL, "api")
        params = {"title": record.title, "authors": record.authors}

        if record.subtitle:
            params.update({"subtitle": record.subtitle})

        if record.type:
            item_type_id = sync_object_with_z(record.type, "itemtype", itemtype=True)
            params.update({"type_id": item_type_id})

        result = requests.get(slash_join(new_url, "record", params=params))
        result.raise_for_status()
        result = result.json()

        if len(result) == 0:
            subject_ids = []
            for subject in record.subjects.all():
                subject_ids.append(sync_object_with_z(subject, "subject"))

            item_type_id = sync_object_with_z(record.type, "itemtype", itemtype=True)
            if record.bibliographic_level:
                bib_id = get_base_id("bibliographiclevel", record.bibliographic_level)
            else:
                bib_id = None

            data = {
                "title": record.title,
                "authors": record.authors,
                "subtitle": record.subtitle,
                "uniform_title": record.uniform_title,
                "notes": record.notes,
                "series": record.series,
                "subjects": subject_ids,
                "type": item_type_id,
                "bibliographic_level": bib_id,
            }
            files = {"image": open(record.image.path, "rb") if record.image else None}
            resp = requests.post(slash_join(new_url, "record"), data=data, files=files)
            resp.raise_for_status()
            return True
