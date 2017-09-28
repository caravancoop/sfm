import reversion

from django.contrib import admin
from .models import Person, PersonName, PersonAlias


class PersonAdmin(admin.ModelAdmin):
    pass


class PersonNameAdmin(admin.ModelAdmin):
    pass


class PersonAliasAdmin(reversion.admin.VersionAdmin):
    pass


admin.site.register(Person, PersonAdmin)
admin.site.register(PersonName, PersonNameAdmin)
admin.site.register(PersonAlias, PersonAliasAdmin)
