import reversion

from django.contrib import admin

from .models import (Association, AssociationStartDate, AssociationEndDate,
                     AssociationOrganization, AssociationArea)


class AssociationAdmin(admin.ModelAdmin):
    pass


class AssociationStartDateAdmin(reversion.admin.VersionAdmin):
    pass


class AssociationEndDateAdmin(reversion.admin.VersionAdmin):
    pass


class AssociationOrganizationAdmin(reversion.admin.VersionAdmin):
    pass


class AssociationAreaAdmin(admin.ModelAdmin):
    pass

admin.site.register(Association, AssociationAdmin)
admin.site.register(AssociationStartDate, AssociationStartDateAdmin)
admin.site.register(AssociationEndDate, AssociationEndDateAdmin)
admin.site.register(AssociationOrganization, AssociationOrganizationAdmin)
admin.site.register(AssociationArea, AssociationAreaAdmin)
