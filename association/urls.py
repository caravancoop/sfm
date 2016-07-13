from django.conf.urls import patterns, url

from .views import (AssociationCreate, AssociationUpdate, AssociationView,
                    association_search, association_csv, AssociationDelete)

urlpatterns = [
    url(r'add/$', AssociationCreate.as_view(), name='add_association'),
    url(r'search/', association_search, name='association_search'),
    url(r'csv/', association_csv, name='association_csv'),
    url(r'delete/(?P<pk>\d+)/$',
        AssociationDelete.as_view(success_url="/association/"),
        name='delete_association'),
    url(r'(?P<pk>\d+)/$', AssociationUpdate.as_view(), name='edit_association'),
    url(r'^$', AssociationView.as_view(), name='association'),
]
