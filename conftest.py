from typing import Any

import pytest
from rest_framework.test import APIClient

from alexandria.utils.management.commands import bootstrap_site


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(transactional_db: Any) -> None:
    """Give all tests database access."""
    pass

# @pytest.fixture(scope='function')
# def django_db_setup(django_db_setup, django_db_blocker):
#     with django_db_blocker.unblock():
#         bootstrap_site.Command().handle()


@pytest.fixture(autouse=True)
def setup_site() -> None:
    """Fixture that configures the site as if it were about to be deployed."""
    bootstrap_site.Command().handle()


@pytest.fixture()
def api_client():
    return APIClient()
