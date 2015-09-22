from django.conf.urls import patterns, url

from .views import OrganizationCreate, OrganizationView, classification_autocomplete

urlpatterns = patterns(
    '',
    url(r'^$', OrganizationView.as_view(), name='organizations'),
    url(r'add/$', OrganizationCreate.as_view(), name="add_organization"),

    url(r'classification/autocomplete', classification_autocomplete,
        name="classification_autocomplete")
)
