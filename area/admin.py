import reversion

from django.contrib import admin

from .models import (Area, AreaName, AreaGeometry, AreaCode, AreaOSMName, AreaOSMId, Code)


class AreaAdmin(admin.ModelAdmin):
    pass


class AreaNameAdmin(reversion.admin.VersionAdmin):
    pass


class AreaGeometryAdmin(admin.ModelAdmin):
    pass


class AreaCodeAdmin(reversion.admin.VersionAdmin):
    pass


class AreaOSMNameAdmin(reversion.admin.VersionAdmin):
    pass


class AreaOSMIdAdmin(reversion.admin.VersionAdmin):
    pass


class CodeAdmin(admin.ModelAdmin):
    pass


admin.site.register(Area, AreaAdmin)
admin.site.register(AreaName, AreaNameAdmin)
admin.site.register(AreaGeometry, AreaGeometryAdmin)
admin.site.register(AreaCode, AreaCodeAdmin)
admin.site.register(AreaOSMName, AreaOSMNameAdmin)
admin.site.register(AreaOSMId, AreaOSMIdAdmin)
admin.site.register(Code, CodeAdmin)
