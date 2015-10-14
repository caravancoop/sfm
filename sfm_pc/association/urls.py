from django.conf.urls import patterns, url

from .views import AssociationCreate, AssociationUpdate, AssociationView

urlpatterns = patterns(
    '',
    url(r'add/$', AssociationCreate.as_view(), name='add_association'),
    url(r'(?P<pk>\d+)/$', AssociationUpdate.as_view(), name='edit_association'),
    url(r'^$', AssociationView.as_view(), name='association'),
)
