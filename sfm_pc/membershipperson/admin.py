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


class MembershipPersonMemberAdmin(reversion.VersionAdmin):
    pass


class MembershipPersonOrganizationMemberAdmin(reversion.VersionAdmin):
    pass


class MembershipPersonOrganizationAdmin(reversion.VersionAdmin):
    pass


class MembershipPersonRoleAdmin(reversion.VersionAdmin):
    pass


class MembershipPersonTitleAdmin(reversion.VersionAdmin):
    pass


class MembershipPersonRankAdmin(reversion.VersionAdmin):
    pass


class MembershipPersonFirstCitedDateAdmin(reversion.VersionAdmin):
    pass


class MembershipPersonLastCitedDateAdmin(reversion.VersionAdmin):
    pass


class MembershipPersonRealStartAdmin(reversion.VersionAdmin):
    pass


class MembershipPersonRealEndAdmin(reversion.VersionAdmin):
    pass


class MembershipPersonStartContextAdmin(reversion.VersionAdmin):
    pass


class MembershipPersonEndContextAdmin(reversion.VersionAdmin):
    pass


class RoleAdmin(reversion.VersionAdmin):
    pass


class RankAdmin(reversion.VersionAdmin):
    pass


class ContextAdmin(reversion.VersionAdmin):
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
