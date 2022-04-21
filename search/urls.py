from django.urls import re_path

from search.views import HaystackSearchView

urlpatterns = [
    re_path(r'^$', HaystackSearchView.as_view(), name='search'),
]
