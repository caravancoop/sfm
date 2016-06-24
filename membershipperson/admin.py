import reversion

from django.contrib import admin

from .models import (MembershipPerson, MembershipPersonMember, MembershipPersonOrganization,
                     MembershipPersonRole, MembershipPersonTitle, MembershipPersonRank,
                     MembershipPersonFirstCitedDate, MembershipPersonLastCitedDate,
                     MembershipPersonRealStart, MembershipPersonRealEnd,
                     MembershipPersonStartContext, MembershipPersonEndContext,
                     Role, Rank, Context)


class MembershipPersonAdmin(admin.ModelAdmin):
    pass


class MembershipPersonMemberAdmin(reversion.admin.VersionAdmin):
    pass


class MembershipPersonOrganizationMemberAdmin(reversion.admin.VersionAdmin):
    pass


class MembershipPersonOrganizationAdmin(reversion.admin.VersionAdmin):
    pass


class MembershipPersonRoleAdmin(reversion.admin.VersionAdmin):
    pass


class MembershipPersonTitleAdmin(reversion.admin.VersionAdmin):
    pass


class MembershipPersonRankAdmin(reversion.admin.VersionAdmin):
    pass


class MembershipPersonFirstCitedDateAdmin(reversion.admin.VersionAdmin):
    pass


class MembershipPersonLastCitedDateAdmin(reversion.admin.VersionAdmin):
    pass


class MembershipPersonRealStartAdmin(reversion.admin.VersionAdmin):
    pass


class MembershipPersonRealEndAdmin(reversion.admin.VersionAdmin):
    pass


class MembershipPersonStartContextAdmin(reversion.admin.VersionAdmin):
    pass


class MembershipPersonEndContextAdmin(reversion.admin.VersionAdmin):
    pass


class RoleAdmin(reversion.admin.VersionAdmin):
    pass


class RankAdmin(reversion.admin.VersionAdmin):
    pass


class ContextAdmin(reversion.admin.VersionAdmin):
    pass


admin.site.register(MembershipPerson, MembershipPersonAdmin)
admin.site.register(MembershipPersonMember, MembershipPersonMemberAdmin)
admin.site.register(MembershipPersonOrganization, MembershipPersonOrganizationAdmin)
admin.site.register(MembershipPersonRole, MembershipPersonRoleAdmin)
admin.site.register(MembershipPersonTitle, MembershipPersonTitleAdmin)
admin.site.register(MembershipPersonRank, MembershipPersonRankAdmin)
admin.site.register(MembershipPersonFirstCitedDate, MembershipPersonFirstCitedDateAdmin)
admin.site.register(MembershipPersonLastCitedDate, MembershipPersonLastCitedDateAdmin)
admin.site.register(MembershipPersonRealStart, MembershipPersonRealStartAdmin)
admin.site.register(MembershipPersonRealEnd, MembershipPersonRealEndAdmin)
admin.site.register(MembershipPersonStartContext, MembershipPersonStartContextAdmin)
admin.site.register(MembershipPersonEndContext, MembershipPersonEndContextAdmin)
admin.site.register(Role, RoleAdmin)
admin.site.register(Rank, RankAdmin)
admin.site.register(Context, ContextAdmin)
