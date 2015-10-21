from django.conf.urls import patterns, url

from .views import (MembershipView, MembershipCreate, MembershipUpdate,
                    rank_autocomplete, role_autocomplete)

urlpatterns = patterns(
    '',
    url(r'^$', MembershipView.as_view(), name='membership'),
    url(r'add/$', MembershipCreate.as_view(), name="add_membership"),
    url(r'(?P<pk>\d+)/$', MembershipUpdate.as_view(), name='edit_person'),
    url(r'rank/autocomplete/', rank_autocomplete, name='rank_autocomplete'),
    url(r'role/autocomplete/', role_autocomplete, name='role_autocomplete'),
)
