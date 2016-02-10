import reversion

from django.contrib import admin

from .models import (Composition, CompositionParent, CompositionChild,
                     CompositionStartDate, CompositionEndDate,
                     CompositionClassification)


class CompositionAdmin(admin.ModelAdmin):
    pass


class CompositionParentAdmin(reversion.VersionAdmin):
    pass


class CompositionChildAdmin(reversion.VersionAdmin):
    pass


class CompositionStartDateAdmin(reversion.VersionAdmin):
    pass


class CompositionEndDateAdmin(reversion.VersionAdmin):
    pass


class CompositionClassificationAdmin(reversion.VersionAdmin):
    pass

admin.site.register(Composition, CompositionAdmin)
admin.site.register(CompositionParent, CompositionParentAdmin)
admin.site.register(CompositionChild, CompositionChildAdmin)
admin.site.register(CompositionStartDate, CompositionStartDateAdmin)
admin.site.register(CompositionEndDate, CompositionEndDateAdmin)
admin.site.register(CompositionClassification, CompositionClassificationAdmin)
