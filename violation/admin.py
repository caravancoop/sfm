import reversion

from django.contrib import admin

from .models import Violation, ViolationStartDate, ViolationEndDate, \
    ViolationLocationDescription, ViolationAdminLevel1, \
    ViolationAdminLevel2, ViolationGeoname, ViolationGeonameId, \
    ViolationLocation, ViolationDescription, ViolationPerpetrator, \
    ViolationPerpetratorOrganization, ViolationType, Type


class ViolationAdmin(admin.ModelAdmin):
    pass


class ViolationStartDateAdmin(reversion.admin.VersionAdmin):
    pass


class ViolationEndDateAdmin(reversion.admin.VersionAdmin):
    pass


class ViolationLocationDescriptionAdmin(reversion.admin.VersionAdmin):
    pass


class ViolationAdminLevel1Admin(reversion.admin.VersionAdmin):
    pass


class ViolationAdminLevel2Admin(reversion.admin.VersionAdmin):
    pass


class ViolationGeonameAdmin(reversion.admin.VersionAdmin):
    pass


class ViolationGeonameIdAdmin(reversion.admin.VersionAdmin):
    pass


class ViolationLocationAdmin(reversion.admin.VersionAdmin):
    pass


class ViolationDescriptionAdmin(reversion.admin.VersionAdmin):
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
admin.site.register(ViolationLocation, ViolationLocationAdmin)
admin.site.register(ViolationGeonameId, ViolationGeonameIdAdmin)
admin.site.register(ViolationGeoname, ViolationGeonameAdmin)
admin.site.register(ViolationAdminLevel2, ViolationAdminLevel2Admin)
admin.site.register(ViolationAdminLevel1, ViolationAdminLevel1Admin)
admin.site.register(ViolationLocationDescription, ViolationLocationDescriptionAdmin)
admin.site.register(ViolationEndDate, ViolationEndDateAdmin)
admin.site.register(ViolationStartDate, ViolationStartDateAdmin)
