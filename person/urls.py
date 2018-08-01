from django.conf.urls import url
from django.views.decorators.cache import cache_page

from person.views import PersonDetail, PersonCreateView, PersonEditView

urlpatterns = [
    url(r'^create/$',
        PersonCreateView.as_view(),
        name="create-person"),
    url(r'edit/(?P<slug>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$', PersonEditBasicsView.as_view(), name='edit-person'),
    url(r'edit/postings/(?P<person_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/(?P<pk>\d+)/$', PersonEditPostingsView.as_view(), name='edit-person-postings'),
    url(r'^view/(?P<slug>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$',
        PersonDetail.as_view(),
        name="view-person"),
]
