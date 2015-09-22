import reversion

from django.contrib import admin

from .models import (Membership, MembershipPerson, MembershipOrganization,
                     MembershipRole, MembershipTitle, MembershipRank, MembershipDate,
                     Role, Rank, Context)


class MembershipAdmin(admin.ModelAdmin):
    pass

class MembershipPersonAdmin(reversion.VersionAdmin):
    pass

class MembershipOrganizationAdmin(reversion.VersionAdmin):
    pass

class MembershipRoleAdmin(reversion.VersionAdmin):
    pass

class MembershipTitleAdmin(reversion.VersionAdmin):
    pass

class MembershipRankAdmin(reversion.VersionAdmin):
    pass

class RoleAdmin(reversion.VersionAdmin):
    pass

class RankAdmin(reversion.VersionAdmin):
    pass

class ContextAdmin(reversion.VersionAdmin):
    pass


admin.site.register(Membership, MembershipAdmin)
admin.site.register(MembershipPerson, MembershipPersonAdmin)
admin.site.register(MembershipOrganization, MembershipOrganizationAdmin)
admin.site.register(MembershipRole, MembershipRoleAdmin)
admin.site.register(MembershipTitle, MembershipTitleAdmin)
admin.site.register(MembershipRank, MembershipRankAdmin)
admin.site.register(Role, RoleAdmin)
admin.site.register(Rank, RankAdmin)
admin.site.register(Context, ContextAdmin)
