import reversion

from django.contrib import admin
from .models import Source


class SourceAdmin(reversion.admin.VersionAdmin):
    pass

admin.site.register(Source, SourceAdmin)
