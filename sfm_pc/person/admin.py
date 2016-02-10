import reversion

from django.contrib import admin
from .models import Person, PersonName, PersonAlias, PersonDeathDate


class PersonAdmin(admin.ModelAdmin):
    pass


class PersonNameAdmin(admin.ModelAdmin):
    pass


class PersonAliasAdmin(reversion.VersionAdmin):
    pass


class PersonDeathDateAdmin(reversion.VersionAdmin):
    pass


admin.site.register(Person, PersonAdmin)
admin.site.register(PersonName, PersonNameAdmin)
admin.site.register(PersonAlias, PersonAliasAdmin)
admin.site.register(PersonDeathDate, PersonDeathDateAdmin)
