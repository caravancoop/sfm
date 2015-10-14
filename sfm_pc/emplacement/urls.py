from django.conf.urls import patterns, url

from .views import EmplacementCreate, EmplacementUpdate, EmplacementView

urlpatterns = patterns(
    '',
    url(r'add/$', EmplacementCreate.as_view(), name='add_emplacement'),
    url(r'(?P<pk>\d+)/$', EmplacementUpdate.as_view(), name='edit_emplacement'),
    url(r'^$', EmplacementView.as_view(), name='emplacement'),
)
