import reversion

from django.contrib import admin
from .models import Organization, ParentOrganization


class OrganizationAdmin(admin.ModelAdmin):
    pass


class ParentOrganizationAdmin(reversion.VersionAdmin):
    pass


admin.site.register(Organization, OrganizationAdmin)
admin.site.register(ParentOrganization, ParentOrganizationAdmin)
