from django.test import Client
from django.urls import reverse

from alexandria.utils.test_helpers import (
    get_default_record,
    get_test_item,
    DEFAULT_PATRON_USER,
    get_default_patron_user,
)


def test_index(client: Client):
    response = client.get(reverse("homepage"))
    assert response.status_code == 200


def test_index_post(client: Client):
    response = client.post(reverse("homepage"), data={"search_text": "wazzzup"})
    assert response.status_code == 302
    assert response.url == "/search/?q=wazzzup"


def test_index_post_without_search_query(client: Client):
    response = client.post(reverse("homepage"), data={"search_text": ""})
    assert response.status_code == 302
    assert response.url == "/search/?q="


class TestCatalog:
    def test_empty_catalog(self, client: Client):
        response = client.get(reverse("search"))
        assert response.status_code == 200

    def test_catalog_search(self, client: Client):
        test_record = get_default_record()
        get_test_item(record=test_record)

        response = client.get(reverse("search"), data={"q": test_record.title})
        assert response.status_code == 200
        paginator_results = response.context["page"].paginator
        assert len(paginator_results.object_list) == 1
        assert test_record in paginator_results.object_list

    def test_catalog_search_without_item(self, client: Client):
        test_record = get_default_record()

        response = client.get(reverse("search"), data={"q": test_record.title})
        assert response.status_code == 200
        paginator_results = response.context["page"].paginator
        assert len(paginator_results.object_list) == 0
        assert test_record not in paginator_results.object_list

    def test_catalog_search_with_inactive_item(self, client: Client):
        test_record = get_default_record()
        get_test_item(record=test_record, is_active=False)

        response = client.get(reverse("search"), data={"q": test_record.title})
        assert response.status_code == 200
        paginator_results = response.context["page"].paginator
        assert len(paginator_results.object_list) == 0
        assert test_record not in paginator_results.object_list

    def test_catalog_ignored_search_terms(self, client: Client):
        response = client.get(reverse("search"), data={"q": "a an the asdf"})
        assert response.status_code == 200
        assert response.context["search_term"] == "asdf"

    def test_non_existant_catalog_detail(self, client: Client):
        user = get_default_patron_user()
        client.force_login(user)

        test_record = get_default_record()
        get_test_item(record=test_record)

        response = client.get(reverse("item_detail", kwargs={"item_id": 44}))
        assert response.status_code == 404
        assert 'record' not in response.context

    def test_catalog_detail(self, client: Client):
        user = get_default_patron_user()
        client.force_login(user)

        test_record = get_default_record()
        get_test_item(record=test_record)

        response = client.get(reverse("item_detail", kwargs={"item_id": test_record.id}))
        assert response.status_code == 200
        assert response.context['record'] == test_record