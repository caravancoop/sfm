import reversion

from django.contrib import admin
from .models import Person, PersonName, PersonAlias, PersonDeathDate




class PersonNameInlineAdmin(admin.TabularInline):
    model = PersonName 

class PersonAliasInlineAdmin(admin.TabularInline):
    model = PersonAlias 

class PersonDeathDateInlineAdmin(admin.TabularInline):
    model = PersonDeathDate

class PersonAdmin(admin.ModelAdmin):
    inlines = [
        PersonNameInlineAdmin,
        PersonAliasInlineAdmin,
        PersonDeathDateInlineAdmin,  
] 


class PersonNameAdmin(reversion.VersionAdmin):
    model = PersonName

class PersonAliasAdmin(reversion.VersionAdmin):
    model = PersonAlias

class PersonDeathDateAdmin(reversion.VersionAdmin):
    model = PersonDeathDate


admin.site.register(Person, PersonAdmin)
