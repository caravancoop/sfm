import reversion

from django.contrib import admin

from .models import (Area, AreaName, AreaGeometry, AreaCode, AreaGeoName, Code)


class AreaAdmin(admin.ModelAdmin):
    pass


class AreaNameAdmin(reversion.VersionAdmin):
    pass


class AreaGeometryAdmin(admin.ModelAdmin):
    pass


class AreaCodeAdmin(reversion.VersionAdmin):
    pass


class AreaGeoNameAdmin(reversion.VersionAdmin):
    pass


class CodeAdmin(admin.ModelAdmin):
    pass

admin.site.register(Area, AreaAdmin)
admin.site.register(AreaName, AreaNameAdmin)
admin.site.register(AreaGeometry, AreaGeometryAdmin)
admin.site.register(AreaCode, AreaCodeAdmin)
admin.site.register(AreaGeoName, AreaGeoNameAdmin)
admin.site.register(Code, CodeAdmin)
