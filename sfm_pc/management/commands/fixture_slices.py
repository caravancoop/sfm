import os
import itertools
from io import StringIO
import json

from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.apps import apps
from django.conf import settings
from django.core import serializers
from django.db.models import Count

from source.models import Source, AccessPoint
from violation.models import Violation
from composition.models import Composition
from membershipperson.models import MembershipPerson, Role, Rank
from membershiporganization.models import MembershipOrganization
from association.models import Association
from emplacement.models import Emplacement
from location.models import Location
from organization.models import Organization
from person.models import Person


MODELS_OF_INTEREST = [
    'Organization',
    'Person',
    'Violation',
    'MembershipOrganization',
    'MembershipPerson',
    'Composition',
    'Location',
    'Composition',
    'Emplacement',
    'Association',
]

class Command(BaseCommand):
    help = 'Make test fixtures based upon slices of existing data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--apps',
            default=MODELS_OF_INTEREST,
            action='append',
            dest='apps',
            help="List of apps to include."
        )

    def model_name(self, m):
        module = m.__module__.split('.')[:-1] # remove .models
        return ".".join(module + [m._meta.object_name])

    def handle(self, *args, **options):
        self.fixture_dir = os.path.join(settings.BASE_DIR, 'tests/fixtures')

        self.sources = set()
        self.people = set()
        self.organizations = set()
        self.locations = set()

        # Things that need to be grabbed first so relations will work:
        #
        # * Violation (get perpetrators, perpetrator organizations, and locations)
        # * Composition (get parent and child organizations)
        # * MembershipPerson (get people and organizations)
        # * MembershipOrganization (get member and organization)
        # * Association (get locations)
        # * Emplacement (get locations)
        #
        # We'll also want all sources from all of these things.

        self.saveViolations()
        self.saveCompositions()
        self.saveMembershipPersons()
        self.saveMembershipOrganizations()
        self.saveAssociations()
        self.saveEmplacements()

        self.savePeople()
        self.saveOrganizations()

        sources = Source.objects.filter(uuid__in=self.sources)
        accesspoints = AccessPoint.objects.filter(source__uuid__in=sources)
        locations = Location.objects.filter(id__in=self.locations)

        source_fixture = serializers.serialize('json', sources)
        accesspoint_fixture = serializers.serialize('json', accesspoints)
        location_fixture = serializers.serialize('json', locations)

        with open(os.path.join(self.fixture_dir, 'source.json'), 'w') as f:
            f.write(source_fixture)

        with open(os.path.join(self.fixture_dir, 'accesspoint.json'), 'w') as f:
            f.write(accesspoint_fixture)

        with open(os.path.join(self.fixture_dir, 'location.json'), 'w') as f:
            f.write(location_fixture)

    def buildOutput(self,
                    queryset,
                    people_fields=[],
                    organization_fields=[],
                    location_fields=[]):
        output = []

        for obj in queryset:

            related = [r for r in dir(obj)
                       if r.startswith(obj._meta.model_name)
                       and r.endswith('_set')]

            output.extend(json.loads(serializers.serialize('json', [obj])))

            for relation in related:

                rel_queryset = getattr(obj, relation).all()
                serialized_values = json.loads(serializers.serialize('json', rel_queryset))

                for value in serialized_values:
                    for v in value['fields']['sources']:
                        self.sources.add(v)

                    if relation in location_fields:
                        self.locations.add(value['fields']['value'])

                    if relation in people_fields:
                        self.people.add(value['fields']['value'])

                    if relation in organization_fields:
                        self.organizations.add(value['fields']['value'])

                output.extend(serialized_values)

        return output

    def writeOutput(self, fixture, name):

        with open(os.path.join(self.fixture_dir, '{}.json'.format(name)), 'w') as f:
            json.dump(fixture, f)

    def saveViolations(self):

        violations = Violation.objects.exclude(violationtype__isnull=True)\
                                      .exclude(violationperpetratorclassification__isnull=True).order_by('?')[:10]

        output = self.buildOutput(violations,
                                  location_fields=['violationlocation_set'],
                                  people_fields=['violationperpetrator_set'],
                                  organization_fields=['violationperpetratororganization_set'])

        self.writeOutput(output, 'violation')

    def saveCompositions(self):
        compositions = Composition.objects.order_by('?')[:10]

        output = self.buildOutput(compositions,
                                  organization_fields=['compositionparent_set', 'compositionchild_set'])

        self.writeOutput(output, 'composition')

    def saveMembershipPersons(self):
        membershippersons = MembershipPerson.objects.order_by('?')[:10]

        output = self.buildOutput(membershippersons,
                                  people_fields=['membershippersonmember_set'],
                                  organization_fields=['membershippersonorganization_set'])

        role_ids = [m['fields']['value'] for m in output if m['model'] == 'membershipperson.membershippersonrole']
        rank_ids = [m['fields']['value'] for m in output if m['model'] == 'membershipperson.membershippersonrank']

        output.extend(self.buildOutput(Role.objects.filter(id__in=role_ids)))
        output.extend(self.buildOutput(Rank.objects.filter(id__in=rank_ids)))

        self.writeOutput(output, 'membershipperson')

    def saveMembershipOrganizations(self):
        membershiporganizations = MembershipOrganization.objects.order_by('?')[:10]

        output = self.buildOutput(membershiporganizations,
                                  organization_fields=['membershiporganizationmember_set', 'membershiporganizationorganization_set'])

        self.writeOutput(output, 'membershiporganization')

    def saveAssociations(self):
        associations = Association.objects.order_by('?')[:10]

        output = self.buildOutput(associations,
                                  organization_fields=['associationorganization_set'],
                                  location_fields=['associationarea_set'])

        self.writeOutput(output, 'association')

    def saveEmplacements(self):
        emplacements = Emplacement.objects.order_by('?')[:10]

        output = self.buildOutput(emplacements,
                                  organization_fields=['emplacementorganization_set'],
                                  location_fields=['emplacementsite_set'])

        self.writeOutput(output, 'emplacement')

    def saveOrganizations(self):
        child_parents = Organization.objects.exclude(child_organization__isnull=True)\
                                            .exclude(parent_organization__isnull=True)[:10]

        compositions = set()

        for organization in child_parents:
            for child in organization.child_organization.all():
                compositions.add(child.object_ref)
            for parent in organization.parent_organization.all():
                compositions.add(parent.object_ref)

        output = self.buildOutput(compositions,
                                  organization_fields=['compositionparent_set',
                                                       'compositionchild_set'])

        organizations = Organization.objects.filter(id__in=self.organizations)

        output.extend(self.buildOutput(organizations))
        output.extend(self.buildOutput(child_parents))

        self.writeOutput(output, 'organization')

    def savePeople(self):
        people = Person.objects.filter(id__in=self.people)
        more_people = Person.objects.annotate(alias_count=Count('personalias'))\
                                    .filter(alias_count__gte=2)[:10]

        memberships = set()

        for person in more_people:
            for member in person.membershippersonmember_set.all():
                memberships.add(member.object_ref)
            for organization in person.memberships.all():
                memberships.add(member.object_ref)

        output = self.buildOutput(memberships,
                                  people_fields=['membershippersonmember_set'],
                                  organization_fields=['membershippersonorganization_set'])

        role_ids = [m['fields']['value'] for m in output if m['model'] == 'membershipperson.membershippersonrole']
        rank_ids = [m['fields']['value'] for m in output if m['model'] == 'membershipperson.membershippersonrank']

        output.extend(self.buildOutput(Role.objects.filter(id__in=role_ids)))
        output.extend(self.buildOutput(Rank.objects.filter(id__in=rank_ids)))

        output.extend(self.buildOutput(people))
        output.extend(self.buildOutput(more_people))

        self.writeOutput(output, 'person')
