from django.conf.urls import patterns, url

from violation.views import ViolationCreate, ViolationUpdate, \
    violation_csv, ViolationDelete, violation_type_autocomplete

urlpatterns = [
    url(r'^create/$', ViolationCreate.as_view(), name="create-event"),
    url(r'csv/', violation_csv, name='violation_csv'),
    url(r'delete/(?P<pk>\d+)/$',
        ViolationDelete.as_view(success_url="/violation/"),
        name='delete_violation'),
    url(r'(?P<pk>\d+)/$', ViolationUpdate.as_view(), name='edit_violation'),
    url(r'type/autocomplete/$', violation_type_autocomplete, name='violation-type-autocomplete'),
    
]
