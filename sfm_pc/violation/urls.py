from django.conf.urls import patterns, url

from .views import ViolationCreate, ViolationUpdate, ViolationView

urlpatterns = patterns(
    '',
    url(r'add/$', ViolationCreate.as_view(), name='add_violation'),
    url(r'(?P<pk>\d+)/$', ViolationUpdate.as_view(), name='edit_violation'),
    url(r'^$', ViolationView.as_view(), name='violation'),
)
