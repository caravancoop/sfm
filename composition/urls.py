from django.conf.urls import url

from .views import CompositionView, CompositionCreate, CompositionUpdate, \
    CompositionDelete, composition_csv

urlpatterns = [
    url(r'^$', CompositionView.as_view(), name='composition'),
    url(r'create/$', CompositionCreate.as_view(), name='create-composition'),
    url(r'csv/', composition_csv, name='compostion_csv'),
    url(r'delete/(?P<pk>\d+)/$',
        CompositionDelete.as_view(success_url="/composition/"),
        name='delete_composition'),
    url(r'(?P<pk>\d+)/$', CompositionUpdate.as_view(), name='edit_composition'),
]
