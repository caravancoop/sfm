import reversion

from django.contrib import admin

from .models import (Area, AreaName, AreaGeometry, AreaCode, AreaGeoname, AreaGeonameId, Code)


class AreaAdmin(admin.ModelAdmin):
    pass


class AreaNameAdmin(reversion.VersionAdmin):
    pass


class AreaGeometryAdmin(admin.ModelAdmin):
    pass


class AreaCodeAdmin(reversion.VersionAdmin):
    pass


class AreaGeonameAdmin(reversion.VersionAdmin):
    pass

class AreaGeonameIdAdmin(reversion.VersionAdmin):
    pass

class CodeAdmin(admin.ModelAdmin):
    pass

admin.site.register(Area, AreaAdmin)
admin.site.register(AreaName, AreaNameAdmin)
admin.site.register(AreaGeometry, AreaGeometryAdmin)
admin.site.register(AreaCode, AreaCodeAdmin)
admin.site.register(AreaGeoname, AreaGeonameAdmin)
admin.site.register(AreaGeonameId, AreaGeonameIdAdmin)
admin.site.register(Code, CodeAdmin)
