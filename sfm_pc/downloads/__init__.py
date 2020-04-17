from .areas import AreaDownload
from .basic import BasicDownload
from .memberships import MembershipOrganizationDownload
from .parentage import ParentageDownload
from .personnel import MembershipPersonDownload
from .sites import SiteDownload
from .sources import SourceDownload


download_classes = {
    'areas': AreaDownload,
    'basic': BasicDownload,
    'memberships': MembershipOrganizationDownload,
    'parentage': ParentageDownload,
    'personnel': MembershipPersonDownload,
    'sites': SiteDownload,
    'sources': SourceDownload,
}
