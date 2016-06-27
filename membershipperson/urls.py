from django.conf.urls import patterns, url

from .views import (MembershipPersonView, MembershipPersonCreate, MembershipPersonUpdate,
                    membership_person_search, rank_autocomplete, role_autocomplete,
                    MembershipPersonDelete, membership_person_csv)

urlpatterns = [
    url(r'^$', MembershipPersonView.as_view(), name='membership'),
    url(r'search/', membership_person_search, name='membership_search'),
    url(r'csv/', membership_person_csv, name='membership_csv'),
    url(r'add/$', MembershipPersonCreate.as_view(), name="add_membership"),
    url(r'delete/(?P<pk>\d+)/$',
        MembershipPersonDelete.as_view(success_url="/membership/"),
        name='delete_membership'),
    url(r'(?P<pk>\d+)/$', MembershipPersonUpdate.as_view(), name='edit_person'),
    url(r'rank/autocomplete/', rank_autocomplete, name='rank_autocomplete'),
    url(r'role/autocomplete/', role_autocomplete, name='role_autocomplete'),
]
