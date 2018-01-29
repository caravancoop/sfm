from django.conf.urls import url
from django.views.decorators.cache import cache_page

from violation.views import ViolationCreate, ViolationUpdate, \
    violation_csv, ViolationDelete, violation_type_autocomplete, \
    ViolationDetail, ViolationList

urlpatterns = [
    url(r'^create/$', ViolationCreate.as_view(), name="create-event"),
    url(r'csv/', violation_csv, name='violation_csv'),
    url(r'delete/(?P<pk>\d+)/$',
        ViolationDelete.as_view(success_url="/violation/"),
        name='delete_violation'),
    url(r'edit/(?P<pk>\d+)/$', ViolationUpdate.as_view(), name='edit_violation'),
    url(r'detail/(?P<pk>\d+)/$', cache_page(60 * 60 * 24)(ViolationDetail.as_view()), name='detail_violation'),
    url(r'list/$', ViolationList.as_view(), name='list-violation'),
    url(r'type/autocomplete/$', violation_type_autocomplete, name='violation-type-autocomplete'),
    
]
