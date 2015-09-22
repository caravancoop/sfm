from django.conf.urls import patterns, url

from .views import MembershipCreate, MembershipView

urlpatterns = patterns(
    '',
    url(r'^$', MembershipView.as_view(), name='membership'),
    url(r'add/$', MembershipCreate.as_view(), name="add_membership"),
)
