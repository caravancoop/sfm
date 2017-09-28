from django.conf.urls import url

from .views import CompositionCreate, CompositionUpdate

urlpatterns = [
    url(r'create/$', CompositionCreate.as_view(), name='create-composition'),
    url(r'(?P<pk>\d+)/$', CompositionUpdate.as_view(), name='edit_composition'),
]
