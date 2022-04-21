from django.urls import re_path
from django.views.decorators.cache import cache_page

from person import views

urlpatterns = [
    re_path(r'^create/$',
        views.PersonCreateView.as_view(),
        name="create-person"),
    re_path(r'create/posting/(?P<person_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$',
        views.PersonCreatePostingView.as_view(),
        name='create-person-posting'),
    re_path(r'edit/(?P<slug>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$',
        views.PersonEditBasicsView.as_view(),
        name='edit-person'),
    re_path(r'edit/postings/(?P<person_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/(?P<pk>\d+)/$',
        views.PersonEditPostingsView.as_view(),
        name='edit-person-postings'),
    re_path(r'delete/(?P<slug>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$',
        views.PersonDeleteView.as_view(),
        name='delete-person'),
    re_path(r'delete/posting/(?P<person_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/(?P<pk>\d+)/$',
        views.PersonDeletePostingView.as_view(),
        name='delete-person-posting'),
    re_path(r'^view/(?P<slug>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$',
        cache_page(60 * 60 * 24)(views.PersonDetail.as_view()),
        name="view-person"),
    re_path(r'autocomplete/$',
        views.person_autocomplete,
        name='person-autocomplete'),
]
