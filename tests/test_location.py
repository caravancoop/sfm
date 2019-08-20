import pytest


@pytest.mark.django_db
def test_location_related_entities():
    pytest.fail()


@pytest.mark.django_db
def test_location_delete():
    pytest.fail()


@pytest.mark.django_db
def test_location_delete_view_with_related_entities():
    # Make sure all the related entities are rendered on the page.
    # Make sure that the confirm button is disabled.
    pytest.fail()


@pytest.mark.django_db
def test_location_delete_view_no_related_entities():
    # Make sure no related entities are rendered on the page.
    # Make sure that the confirm button is enabled.
    pytest.fail()
