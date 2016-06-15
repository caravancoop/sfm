import reversion

from django.contrib import admin
from .models import (Organization, OrganizationName, OrganizationAlias,
                     OrganizationClassification, OrganizationFoundingDate,
                     OrganizationRealFounding, Classification)


class OrganizationAdmin(admin.ModelAdmin):
    pass


class OrganizationNameAdmin(reversion.VersionAdmin):
    pass


class OrganizationAliasAdmin(reversion.VersionAdmin):
    pass


class OrganizationClassificationAdmin(reversion.VersionAdmin):
    pass


class OrganizationFoundingDateAdmin(reversion.VersionAdmin):
    pass


class OrganizationRealFoundingAdmin(reversion.VersionAdmin):
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
