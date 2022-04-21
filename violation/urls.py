from django.urls import re_path
from django.views.decorators.cache import cache_page

from violation import views

urlpatterns = [
    re_path(r'csv/', views.violation_csv, name='violation_csv'),
    re_path(r'^view/(?P<slug>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$',
        cache_page(60 * 60 * 24)(views.ViolationDetail.as_view()),
        name="view-violation"),
    re_path(r'^edit/(?P<slug>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$',
        views.ViolationEditBasicsView.as_view(),
        name="edit-violation"),
    re_path(r'^edit/locations/(?P<slug>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$',
        views.ViolationEditLocationsView.as_view(),
        name="edit-violation-locations"),
    re_path(r'^delete/(?P<slug>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$',
        views.ViolationDeleteView.as_view(),
        name="delete-violation"),
    re_path(r'^create/$',
        views.ViolationCreateBasicsView.as_view(),
        name="create-violation"),
    re_path(r'type/autocomplete/$', views.violation_type_autocomplete, name='violation-type-autocomplete'),
    re_path(r'classification/autocomplete/$',
        views.violation_perpetrator_classification_autocomplete,
        name='perpetrator-classification-autocomplete'),
]
