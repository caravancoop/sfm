from django.conf.urls import url

from .views import (EmplacementCreate, EmplacementUpdate, EmplacementView,
                    emplacement_search, emplacement_csv, EmplacementDelete)

urlpatterns = [
    url(r'add/$', EmplacementCreate.as_view(), name='add_emplacement'),
    url(r'search/', emplacement_search, name='emplacement_search'),
    url(r'csv/', emplacement_csv, name='emplacement_csv'),
    url(r'delete/(?P<pk>\d+)/$',
        EmplacementDelete.as_view(success_url="/emplacement/"),
        name='delete_emplacement'),
    url(r'(?P<pk>\d+)/$', EmplacementUpdate.as_view(), name='edit_emplacement'),
    url(r'^$', EmplacementView.as_view(), name='emplacement'),
]
