from django.conf.urls import patterns, url

from .views import MembershipCreate

urlpatterns = patterns(
    '',
    url(r'add/$', MembershipCreate.as_view(), name="add_membership"),
)
