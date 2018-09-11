import reversion

from django.contrib import admin

from .models import (Emplacement, EmplacementStartDate, EmplacementEndDate,
                     EmplacementOrganization, EmplacementSite)


class EmplacementAdmin(admin.ModelAdmin):
    pass


class EmplacementStartDateAdmin(reversion.admin.VersionAdmin):
    pass


class EmplacementEndDateAdmin(reversion.admin.VersionAdmin):
    pass


class EmplacementOrganizationAdmin(reversion.admin.VersionAdmin):
    pass


class EmplacementSiteAdmin(admin.ModelAdmin):
    pass


admin.site.register(Emplacement, EmplacementAdmin)
admin.site.register(EmplacementStartDate, EmplacementStartDateAdmin)
admin.site.register(EmplacementEndDate, EmplacementEndDateAdmin)
admin.site.register(EmplacementOrganization, EmplacementOrganizationAdmin)
admin.site.register(EmplacementSite, EmplacementSiteAdmin)
