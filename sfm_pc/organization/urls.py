from django.conf.urls import patterns, url

from .views import OrganizationCreate

urlpatterns = patterns(
    '',
    url(r'add/$', OrganizationCreate.as_view(), name="add_organization"),
)
