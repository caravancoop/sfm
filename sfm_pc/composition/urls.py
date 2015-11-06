from django.conf.urls import patterns, url

from .views import (CompositionView, CompositionCreate, CompositionUpdate,
                    composition_search, CompositionDelete, composition_csv)

urlpatterns = patterns(
    '',
    url(r'^$', CompositionView.as_view(), name='composition'),
    url(r'add/$', CompositionCreate.as_view(), name='add_composition'),
    url(r'search/', composition_search, name='composition_search'),
    url(r'csv/', composition_csv, name='compostion_csv'),
    url(r'delete/(?P<pk>\d+)/$',
        CompositionDelete.as_view(success_url="/composition/"),
        name='delete_composition'),
    url(r'(?P<pk>\d+)/$', CompositionUpdate.as_view(), name='edit_composition'),
)
