import reversion

from django.contrib import admin
from .models import Person, PersonName, PersonAlias, PersonDeathDate




class PersonNameInlineAdmin(admin.TabularInline):
    model = PersonName 

class PersonAliasInlineAdmin(admin.TabularInline):
    model = PersonAlias 

class PersonNotesInlineAdmin(admin.TabularInline):
    model = PersonNotes

class PersonAdmin(admin.ModelAdmin):
    inlines = [
        PersonNameInlineAdmin,
        PersonAliasInlineAdmin,
        PersonNotesInlineAdmin,  
] 


class PersonNameAdmin(reversion.VersionAdmin):
    model = PersonName

class PersonAliasAdmin(reversion.VersionAdmin):
    model = PersonAlias

class PersonNotesAdmin(reversion.VersionAdmin):
    model = PersonNotes


admin.site.register(Person, PersonAdmin)
