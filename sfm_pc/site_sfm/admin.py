import reversion

from django.contrib import admin

from .models import (Site, SiteName, SiteAdminLevel1, SiteAdminLevel2, SiteCoordinates,
                     SiteGeoname, SiteGeonameId)

class SiteAdmin(admin.ModelAdmin):
    pass

class SiteNameAdmin(reversion.VersionAdmin):
    pass

class SiteAdminLevel1Admin(reversion.VersionAdmin):
    pass

class SiteAdminLevel2Admin(reversion.VersionAdmin):
    pass

class SiteCoordinatesAdmin(reversion.VersionAdmin):
    pass

class SiteGeonameAdmin(reversion.VersionAdmin):
    pass

class SiteGeonameIdAdmin(reversion.VersionAdmin):
    pass

admin.site.register(Site, SiteAdmin)
admin.site.register(SiteName, SiteNameAdmin)
admin.site.register(SiteAdminLevel1, SiteAdminLevel1Admin)
admin.site.register(SiteAdminLevel2, SiteAdminLevel2Admin)
admin.site.register(SiteCoordinates, SiteCoordinatesAdmin)
admin.site.register(SiteGeoname, SiteGeonameAdmin)
admin.site.register(SiteGeonameId, SiteGeonameIdAdmin)
