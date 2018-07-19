from django.conf.urls import url
from django.views.decorators.cache import cache_page

from person.views import alias_autocomplete, PersonUpdateView, \
    PersonDetail, PersonCreateView

urlpatterns = [
    url(r'^create/$',
        PersonCreateView.as_view(),
        name="create-person"),
    url(r'alias/autocomplete/', alias_autocomplete, name='person-alias-autocomplete'),
    url(r'update/(?P<slug>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$', PersonUpdateView.as_view(), name='update-person'),
    url(r'^view/(?P<slug>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$',
        cache_page(60 * 60 * 24)(PersonDetail.as_view()),
        name="view-person"),
]
