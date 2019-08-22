from django.conf.urls import url
from django.views.decorators.cache import cache_page

from person import views

urlpatterns = [
    url(r'^create/$',
        views.PersonCreateView.as_view(),
        name="create-person"),
    url(r'create/posting/(?P<person_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$',
        views.PersonCreatePostingView.as_view(),
        name='create-person-posting'),
    url(r'edit/(?P<slug>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$',
        views.PersonEditBasicsView.as_view(),
        name='edit-person'),
    url(r'edit/postings/(?P<person_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/(?P<pk>\d+)/$',
        views.PersonEditPostingsView.as_view(),
        name='edit-person-postings'),
    url(r'delete/(?P<slug>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$',
        views.PersonDeleteView.as_view(),
        name='delete-person'),
    url(r'delete/posting/(?P<person_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/(?P<pk>\d+)/$',
        views.PersonDeletePostingView.as_view(),
        name='delete-person-posting'),
    url(r'^view/(?P<slug>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$',
        views.PersonDetail.as_view(),
        name="view-person"),
    url(r'autocomplete/$',
        views.person_autocomplete,
        name='person-autocomplete'),
]
