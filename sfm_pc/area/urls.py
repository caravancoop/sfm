from django.conf.urls import patterns, url

from .views import AreaCreate, AreaUpdate

urlpatterns = patterns(
    '',
    url(r'add/$', AreaCreate.as_view(), name='add_area'),
    url(r'(?P<pk>\d+)/$', AreaUpdate.as_view(), name='edit_area'),
)
