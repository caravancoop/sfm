import reversion

from django.contrib import admin

from .models import (Composition, CompositionParent, CompositionChild,
                     CompositionStartDate, CompositionEndDate,
                     CompositionClassification)


class CompositionAdmin(admin.ModelAdmin):
    pass


class CompositionParentAdmin(reversion.admin.VersionAdmin):
    pass


class CompositionChildAdmin(reversion.admin.VersionAdmin):
    pass


class CompositionStartDateAdmin(reversion.admin.VersionAdmin):
    pass


class CompositionEndDateAdmin(reversion.admin.VersionAdmin):
    pass


class CompositionClassificationAdmin(reversion.admin.VersionAdmin):
    pass

admin.site.register(Composition, CompositionAdmin)
admin.site.register(CompositionParent, CompositionParentAdmin)
admin.site.register(CompositionChild, CompositionChildAdmin)
admin.site.register(CompositionStartDate, CompositionStartDateAdmin)
admin.site.register(CompositionEndDate, CompositionEndDateAdmin)
admin.site.register(CompositionClassification, CompositionClassificationAdmin)
