from django.conf.urls import url

from membershipperson.views import MembershipPersonCreate, \
    MembershipPersonUpdate, rank_autocomplete, role_autocomplete, \
    membership_person_csv

urlpatterns = [
    url(r'^create/$', MembershipPersonCreate.as_view(), name="create-membership"),
    url(r'csv/', membership_person_csv, name='membership-csv'),
    url(r'(?P<pk>\d+)/$', MembershipPersonUpdate.as_view(), name='edit-membership'),
    url(r'rank/autocomplete/', rank_autocomplete, name='rank-autocomplete'),
    url(r'role/autocomplete/', role_autocomplete, name='role-autocomplete'),
]
