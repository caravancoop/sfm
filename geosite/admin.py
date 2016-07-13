import reversion

from django.contrib import admin

from .models import (Geosite, GeositeName, GeositeAdminLevel1,
                     GeositeAdminLevel2, GeositeCoordinates,
                     GeositeGeoname, GeositeGeonameId)


class GeositeAdmin(admin.ModelAdmin):
    pass


class GeositeNameAdmin(reversion.admin.VersionAdmin):
    pass


class GeositeAdminLevel1Admin(reversion.admin.VersionAdmin):
    pass


class GeositeAdminLevel2Admin(reversion.admin.VersionAdmin):
    pass


class GeositeCoordinatesAdmin(reversion.admin.VersionAdmin):
    pass


class GeositeGeonameAdmin(reversion.admin.VersionAdmin):
    pass


class GeositeGeonameIdAdmin(reversion.admin.VersionAdmin):
    pass

admin.site.register(Geosite, GeositeAdmin)
admin.site.register(GeositeName, GeositeNameAdmin)
admin.site.register(GeositeAdminLevel1, GeositeAdminLevel1Admin)
admin.site.register(GeositeAdminLevel2, GeositeAdminLevel2Admin)
admin.site.register(GeositeCoordinates, GeositeCoordinatesAdmin)
admin.site.register(GeositeGeoname, GeositeGeonameAdmin)
admin.site.register(GeositeGeonameId, GeositeGeonameIdAdmin)
