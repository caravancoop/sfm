from django.conf.urls import patterns, url

from .views import PersonView, PersonUpdate, PersonCreate, FieldUpdate

urlpatterns = patterns(
    '',
    url(r'view/(?P<field_type>[a-zA-Z]+)/' +
        '(?P<person_id>[0-9]+)/',
        FieldUpdate.as_view(),
        name="update_field"),
    url(r'add/$', PersonCreate.as_view(), name='add_person'),
    url(r'^$', PersonView.as_view(), name='person'),
    url(r'(?P<pk>\d+)/$', PersonUpdate.as_view(), name='edit_person'),
)
