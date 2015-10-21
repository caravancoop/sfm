import reversion

from django.contrib import admin

from .models import (Membership, MembershipPersonMember, MembershipOrganizationMember,
                     MembershipOrganization, MembershipRole, MembershipTitle,
                     MembershipRank, MembershipDate, MembershipRealStart,
                     MembershipRealEnd, MembershipStartContext, MembershipEndContext,
                     Role, Rank, Context)


class MembershipAdmin(admin.ModelAdmin):
    pass

class MembershipPersonMemberAdmin(reversion.VersionAdmin):
    pass

class MembershipOrganizationMemberAdmin(reversion.VersionAdmin):
    pass

class MembershipOrganizationAdmin(reversion.VersionAdmin):
    pass

class MembershipRoleAdmin(reversion.VersionAdmin):
    pass

class MembershipTitleAdmin(reversion.VersionAdmin):
    pass

class MembershipRankAdmin(reversion.VersionAdmin):
    pass

class MembershipDateAdmin(reversion.VersionAdmin):
    pass

class MembershipRealStartAdmin(reversion.VersionAdmin):
    pass

class MembershipRealEndAdmin(reversion.VersionAdmin):
    pass

class MembershipStartContextAdmin(reversion.VersionAdmin):
    pass

class MembershipEndContextAdmin(reversion.VersionAdmin):
    pass

class RoleAdmin(reversion.VersionAdmin):
    pass

class RankAdmin(reversion.VersionAdmin):
    pass

class ContextAdmin(reversion.VersionAdmin):
    pass


admin.site.register(Membership, MembershipAdmin)
admin.site.register(MembershipPersonMember, MembershipPersonMemberAdmin)
admin.site.register(MembershipOrganizationMember, MembershipOrganizationMemberAdmin)
admin.site.register(MembershipOrganization, MembershipOrganizationAdmin)
admin.site.register(MembershipRole, MembershipRoleAdmin)
admin.site.register(MembershipTitle, MembershipTitleAdmin)
admin.site.register(MembershipRank, MembershipRankAdmin)
admin.site.register(MembershipDate, MembershipDateAdmin)
admin.site.register(MembershipRealStart, MembershipRealStartAdmin)
admin.site.register(MembershipRealEnd, MembershipRealEndAdmin)
admin.site.register(MembershipStartContext, MembershipStartContextAdmin)
admin.site.register(MembershipEndContext, MembershipEndContextAdmin)
admin.site.register(Role, RoleAdmin)
admin.site.register(Rank, RankAdmin)
admin.site.register(Context, ContextAdmin)
