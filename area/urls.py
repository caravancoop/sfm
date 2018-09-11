from django.conf.urls import url

from .views import (AreaCreate, AreaUpdate, AreaView, area_search,
                    area_autocomplete, code_autocomplete, area_csv, AreaDelete)

urlpatterns = [
    url(r'add/$', AreaCreate.as_view(), name='add_area'),
    url(r'search/', area_search, name='area_search'),
    url(r'csv/', area_csv, name='area_csv'),
    url(r'delete/(?P<pk>\d+)/$',
        AreaDelete.as_view(success_url="/area/"),
        name='delete_area'),
    url(r'(?P<pk>\d+)/$', AreaUpdate.as_view(), name='edit_area'),
    url(r'^$', AreaView.as_view(), name='area'),
    url(r'code/autocomplete', code_autocomplete,
        name="code_autocomplete"),
    url(r'autocomplete', area_autocomplete,
        name="area_autocomplete"),
]
