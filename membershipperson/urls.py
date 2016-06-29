from django.conf.urls import patterns, url

from membershipperson.views import MembershipPersonCreate, \
    MembershipPersonUpdate, rank_autocomplete, role_autocomplete, \
    membership_person_csv

urlpatterns = [
    url(r'^create/$', MembershipPersonCreate.as_view(), name="create-membership"),
    url(r'csv/', membership_person_csv, name='membership_csv'),
    url(r'(?P<pk>\d+)/$', MembershipPersonUpdate.as_view(), name='edit_person'),
    url(r'rank/autocomplete/', rank_autocomplete, name='rank_autocomplete'),
    url(r'role/autocomplete/', role_autocomplete, name='role_autocomplete'),
]
