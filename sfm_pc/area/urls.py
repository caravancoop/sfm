from django.conf.urls import patterns, url

from .views import (AreaCreate, AreaUpdate, AreaView, area_autocomplete,
                    code_autocomplete)

urlpatterns = patterns(
    '',
    url(r'add/$', AreaCreate.as_view(), name='add_area'),
    url(r'(?P<pk>\d+)/$', AreaUpdate.as_view(), name='edit_area'),
    url(r'^$', AreaView.as_view(), name='area'),
    url(r'code/autocomplete', code_autocomplete,
        name="code_autocomplete"),
    url(r'autocomplete', area_autocomplete,
        name="area_autocomplete"),
)
