from django.conf.urls import url
from django.views.decorators.cache import cache_page

from violation.views import violation_csv, violation_type_autocomplete, \
    ViolationDetail, ViolationEditBasicsView

urlpatterns = [
    url(r'csv/', violation_csv, name='violation_csv'),
    url(r'^view/(?P<slug>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$',
        ViolationDetail.as_view(),
        name="view-violation"),
    url(r'^edit/(?P<slug>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$',
        ViolationEditBasicsView.as_view(),
        name="edit-violation"),
    url(r'type/autocomplete/$', violation_type_autocomplete, name='violation-type-autocomplete'),
]
