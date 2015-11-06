from django.conf.urls import patterns, url

from .views import (MembershipView, MembershipCreate, MembershipUpdate,
                    membership_search, rank_autocomplete, role_autocomplete,
                    MembershipDelete)

urlpatterns = patterns(
    '',
    url(r'^$', MembershipView.as_view(), name='membership'),
    url(r'search/', membership_search, name='membership_search'),
    url(r'add/$', MembershipCreate.as_view(), name="add_membership"),
    url(r'delete/(?P<pk>\d+)/$',
        MembershipDelete.as_view(success_url="/membership/"),
        name='delete_membership'),
    url(r'(?P<pk>\d+)/$', MembershipUpdate.as_view(), name='edit_person'),
    url(r'rank/autocomplete/', rank_autocomplete, name='rank_autocomplete'),
    url(r'role/autocomplete/', role_autocomplete, name='role_autocomplete'),
)
