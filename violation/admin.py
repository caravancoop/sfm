import reversion

from django.contrib import admin

from .models import Violation, ViolationStartDate, ViolationEndDate, \
    ViolationLocationDescription, ViolationDescription, ViolationPerpetrator, \
    ViolationPerpetratorOrganization, ViolationType, Type, ViolationSite


class ViolationAdmin(admin.ModelAdmin):
    pass


class ViolationStartDateAdmin(reversion.admin.VersionAdmin):
    pass


class ViolationEndDateAdmin(reversion.admin.VersionAdmin):
    pass


class ViolationDescriptionAdmin(reversion.admin.VersionAdmin):
    pass


class ViolationLocationDescriptionAdmin(reversion.admin.VersionAdmin):
    pass


class ViolationSiteAdmin(reversion.admin.VersionAdmin):
    pass


class ViolationPerpetratorAdmin(reversion.admin.VersionAdmin):
    pass


class ViolationPerpetratorOrganizationAdmin(reversion.admin.VersionAdmin):
    pass


class ViolationTypeAdmin(reversion.admin.VersionAdmin):
    pass


class TypeAdmin(reversion.admin.VersionAdmin):
    pass


admin.site.register(Type, TypeAdmin)
admin.site.register(ViolationType, ViolationTypeAdmin)
admin.site.register(ViolationPerpetratorOrganization, ViolationPerpetratorOrganizationAdmin)
admin.site.register(ViolationPerpetrator, ViolationPerpetratorAdmin)
admin.site.register(ViolationDescription, ViolationDescriptionAdmin)
admin.site.register(ViolationLocationDescription, ViolationLocationDescriptionAdmin)
admin.site.register(ViolationSite, ViolationSiteAdmin)
admin.site.register(ViolationEndDate, ViolationEndDateAdmin)
admin.site.register(ViolationStartDate, ViolationStartDateAdmin)
