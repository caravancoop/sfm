from django.conf.urls import url

from search.views import search

urlpatterns = [
    url(r'^$', search, name="search"),
]
