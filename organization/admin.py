import reversion

from django.contrib import admin
from .models import (Organization, OrganizationName, OrganizationAlias,
                     OrganizationClassification, OrganizationFoundingDate,
                     OrganizationRealFounding, Classification)


class OrganizationAdmin(admin.ModelAdmin):
    pass


class OrganizationNameAdmin(reversion.admin.VersionAdmin):
    pass


class OrganizationAliasAdmin(reversion.admin.VersionAdmin):
    pass


class OrganizationClassificationAdmin(reversion.admin.VersionAdmin):
    pass


class OrganizationFoundingDateAdmin(reversion.admin.VersionAdmin):
    pass


class OrganizationRealFoundingAdmin(reversion.admin.VersionAdmin):
    pass


class ClassificationAdmin(admin.ModelAdmin):
    pass


admin.site.register(Organization, OrganizationAdmin)
admin.site.register(OrganizationName, OrganizationNameAdmin)
admin.site.register(OrganizationAlias, OrganizationAliasAdmin)
admin.site.register(OrganizationClassification, OrganizationClassificationAdmin)
admin.site.register(OrganizationFoundingDate, OrganizationFoundingDateAdmin)
admin.site.register(OrganizationRealFounding, OrganizationRealFoundingAdmin)
admin.site.register(Classification, ClassificationAdmin)
