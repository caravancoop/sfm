from django.conf.urls import url

from membershiporganization.views import MembershipOrganizationCreate

urlpatterns = [
    url(r'^create/$', MembershipOrganizationCreate.as_view(), name="create-organization-membership"),
]
