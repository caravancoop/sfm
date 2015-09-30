from django.conf.urls import patterns, url

from .views import CompositionView, CompositionCreate, CompositionUpdate

urlpatterns = patterns(
    '',
    url(r'^$', CompositionView.as_view(), name='composition'),
    url(r'add/$', CompositionCreate.as_view(), name='add_composition'),
    url(r'(?P<pk>\d+)/$', CompositionUpdate.as_view(), name='edit_composition'),
)
