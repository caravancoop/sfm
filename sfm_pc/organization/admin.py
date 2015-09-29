import reversion

from django.contrib import admin
from .models import (Organization, OrganizationName, OrganizationAlias,
                     OrganizationClassification, OrganizationFoundingDate,
                     OrganizationDissolutionDate, OrganizationRealFounding,
                     OrganizationRealDissolution, OrganizationComposition,
                     OrganizationCompositionParent, OrganizationCompositionChild,
                     OrganizationCompositionStartDate, OrganizationCompositionEndDate,
                     OrganizationCompositionClassification, Classification)


class OrganizationAdmin(admin.ModelAdmin):
    pass

class OrganizationNameAdmin(reversion.VersionAdmin):
    pass

class OrganizationAliasAdmin(reversion.VersionAdmin):
    pass

class OrganizationClassificationAdmin(reversion.VersionAdmin):
    pass

class OrganizationFoundingDateAdmin(reversion.VersionAdmin):
    pass

class OrganizationDissolutionDateAdmin(reversion.VersionAdmin):
    pass

class OrganizationRealFoundingAdmin(reversion.VersionAdmin):
    pass

class OrganizationRealDissolutionAdmin(reversion.VersionAdmin):
    pass

class OrganizationCompositionAdmin(admin.ModelAdmin):
    pass

class OrganizationCompositionParentAdmin(reversion.VersionAdmin):
    pass

class OrganizationCompositionChildAdmin(reversion.VersionAdmin):
    pass

class OrganizationCompositionStartDateAdmin(reversion.VersionAdmin):
    pass

class OrganizationCompositionEndDateAdmin(reversion.VersionAdmin):
    pass

class OrganizationCompositionClassificationAdmin(reversion.VersionAdmin):
    pass

class ClassificationAdmin(admin.ModelAdmin):
    pass


admin.site.register(Organization, OrganizationAdmin)
admin.site.register(OrganizationName, OrganizationNameAdmin)
admin.site.register(OrganizationAlias, OrganizationAliasAdmin)
admin.site.register(OrganizationClassification, OrganizationClassificationAdmin)
admin.site.register(OrganizationFoundingDate, OrganizationFoundingDateAdmin)
admin.site.register(OrganizationDissolutionDate, OrganizationDissolutionDateAdmin)
admin.site.register(OrganizationRealFounding, OrganizationRealFoundingAdmin)
admin.site.register(OrganizationRealDissolution, OrganizationRealDissolutionAdmin)
admin.site.register(OrganizationComposition, OrganizationCompositionAdmin)
admin.site.register(OrganizationCompositionParent, OrganizationCompositionParentAdmin)
admin.site.register(OrganizationCompositionChild, OrganizationCompositionChildAdmin)
admin.site.register(OrganizationCompositionStartDate, OrganizationCompositionStartDateAdmin)
admin.site.register(OrganizationCompositionEndDate, OrganizationCompositionEndDateAdmin)
admin.site.register(OrganizationCompositionClassification,
                    OrganizationCompositionClassificationAdmin)
admin.site.register(Classification, ClassificationAdmin)
