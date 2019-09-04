import threading
import uuid
import re

import requests

import reversion

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse_lazy
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.utils.translation import gettext as _
from django.utils.translation import ngettext
from django_date_extensions.fields import ApproximateDateField

from sfm_pc.utils import VersionsMixin


def get_deleted_user():
    return get_user_model().objects.get_or_create(username='deleted user')[0]


@reversion.register(follow=['accesspoint_set'])
class Source(models.Model, VersionsMixin):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    title = models.TextField()
    publication = models.TextField(null=True)
    publication_country = models.CharField(max_length=1000, null=True)
    published_on = ApproximateDateField()
    source_url = models.URLField(max_length=1000, null=True, blank=True)

    date_updated = models.DateTimeField(auto_now=True)
    date_added = models.DateTimeField(auto_now_add=True)

    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.SET(get_deleted_user))

    def __str__(self):
        if self.title is None:
            return ""
        return self.title

    def get_absolute_url(self):
        from django.core.urlresolvers import reverse
        return reverse('view-source', args=[self.uuid])

    @property
    def related_entities(self):
        """
        Return a list of dicts representing the access points that are linked
        to this source.

        Dicts must include the following metadata:
            - name
            - archive_url
            - page_number
            - access_date
            - url (of the Edit view for the access point)
        """
        related_entities = []
        for point in self.accesspoint_set.all():
            related_entities.append({
                'name': str(point),
                'archive_url': point.archive_url,
                'page_number': point.page_number,
                'accessed_on': point.accessed_on,
                'url': reverse_lazy(
                    'update-access-point',
                    kwargs={'source_id': self.uuid, 'pk': point.uuid}
                )
            })
        return related_entities

    @property
    def revert_url(self):
        from django.core.urlresolvers import reverse
        return reverse('revert-source', args=[self.uuid])


@reversion.register()
class AccessPoint(models.Model, VersionsMixin):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    page_number = models.CharField(max_length=255, null=True, blank=True)
    accessed_on = models.DateField(null=True)
    archive_url = models.URLField(max_length=1000, null=True,)
    source = models.ForeignKey(Source, null=True, to_field='uuid')

    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.SET(get_deleted_user))

    def __str__(self):
        point_name = self.archive_timestamp
        if self.page_number:
            # Check if the page number is a range; if so, indicate to ngettext
            # that the string should be plural. See:
            # https://docs.djangoproject.com/en/2.2/topics/i18n/translation/#pluralization
            is_range = 2 if ('-' in self.page_number or ', ' in self.page_number) else 1
            # Translators: This fragment references to the page numbers in an access point.
            pages_str = ngettext(
                '(Page %(pages)s)',
                '(Pages %(pages)s)',
                is_range
            ) % {
                'pages': self.page_number
            }
            point_name += ' ' + pages_str
        if self.accessed_on:
            point_name += ' - ' + _('Accessed on %(date)s') % {'date': self.accessed_on}
        return point_name

    @property
    def archive_timestamp(self):
        """Given an access point archive_url, parse the timestamp."""
        match = re.search(r"web\.archive\.org/web/(\d{14})/", self.archive_url)
        if match:
            return match.group(1)
        else:
            return _('No timestamp')

    @property
    def related_entities(self):
        """
        Return a list of dicts of all entities that are evidenced by this
        access point.

        Dicts must have the following keys:
            - name
            - entity_type
            - field_name
            - url (a link to edit the entity)
        """
        related_entities = []

        for prop in dir(self):
            if prop.endswith('_related'):
                related = getattr(self, prop).all()
                if related:
                    for entity in related:
                        record_type = entity.object_ref._meta.object_name
                        entity_metadata = {
                            'name': str(entity),
                            'record_type': record_type,
                            'field_name': entity._meta.model_name.replace(record_type.lower(), '').title(),
                            'value': entity.value,
                            'url': None
                        }
                        # Links for top-level entities
                        if record_type in ['Organization', 'Person', 'Violation']:
                            entity_metadata['url'] = reverse_lazy(
                                'edit-{}'.format(record_type.lower()),
                                args=[entity.object_ref.uuid]
                            )
                        # Standardized relationship links
                        elif record_type in ['Emplacement', 'Association']:
                            entity_metadata['url'] = reverse_lazy(
                                'edit-organization-{}'.format(record_type.lower()),
                                kwargs={
                                    'organization_id': entity.object_ref.organization.get_value().value.uuid,
                                    'pk': entity.object_ref.pk
                                }
                            )
                        # Irregular relationship links
                        elif record_type == 'Composition':
                            entity_metadata['url'] = reverse_lazy(
                                'edit-organization-composition',
                                kwargs={
                                    'organization_id': entity.object_ref.parent.get_value().value.uuid,
                                    'pk': entity.object_ref.pk
                                }
                            )
                        elif record_type == 'MembershipPerson':
                            entity_metadata['url'] = reverse_lazy(
                                'edit-organization-personnel',
                                kwargs={
                                    'organization_id': entity.object_ref.organization.get_value().value.uuid,
                                    'pk': entity.pk
                                }
                            )
                        elif record_type == 'MembershipOrganization':
                            entity_metadata['url'] = reverse_lazy(
                                'edit-organization-membership',
                                kwargs={
                                    'organization_id': entity.object_ref.organization.get_value().value.uuid,
                                    'pk': entity.pk
                                }
                            )
                        related_entities.append(entity_metadata)
        return related_entities


def archive_source_url(source):

    if source.source_url:
        wayback_host = 'http://web.archive.org'
        save_url = '{0}/save/{1}'.format(wayback_host, source.source_url)
        archived = requests.get(save_url)
        source.archive_url = '{0}{1}'.format(wayback_host,
                                             archived.headers['Content-Location'])
        source.save()

#@receiver(post_save, sender=Source)
def get_archived_url(sender, **kwargs):

    source = kwargs['instance']

    thread = threading.Thread(target=archive_source_url,
                              args=[source])
    thread.start()
