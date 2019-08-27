from django.conf.urls import url
from django.views.decorators.cache import cache_page

from violation import views

urlpatterns = [
    url(r'csv/', views.violation_csv, name='violation_csv'),
    url(r'^view/(?P<slug>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$',
        views.ViolationDetail.as_view(),
        name="view-violation"),
    url(r'^edit/(?P<slug>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$',
        views.ViolationEditBasicsView.as_view(),
        name="edit-violation"),
    url(r'^edit/locations/(?P<slug>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$',
        views.ViolationEditLocationsView.as_view(),
        name="edit-violation-locations"),
    url(r'^delete/(?P<slug>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$',
        views.ViolationDeleteView.as_view(),
        name="delete-violation"),
    url(r'^create/$',
        views.ViolationCreateBasicsView.as_view(),
        name="create-violation"),
    url(r'type/autocomplete/$', views.violation_type_autocomplete, name='violation-type-autocomplete'),
    url(r'classification/autocomplete/$',
        views.violation_perpetrator_classification_autocomplete,
        name='perpetrator-classification-autocomplete'),
]
