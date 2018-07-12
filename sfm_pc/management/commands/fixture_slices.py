import os
import itertools
from io import StringIO
import json

from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.apps import apps
from django.conf import settings
from django.core import serializers

from source.models import Source, AccessPoint

class Command(BaseCommand):
    help = 'Make test fixtures based upon slices of existing data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--apps',
            default=['Organization', 'Person', 'Violation', 'MembershipOrganization', 'MembershipPerson'],
            action='append',
            dest='apps',
            help="List of apps to include."
        )
        parser.add_argument(
            '--refresh',
            action='store_true',
            dest='refresh',
            default=False,
            help='Refresh all views'
        )

    def model_name(self, m):
        module = m.__module__.split('.')[:-1] # remove .models
        return ".".join(module + [m._meta.object_name])

    def handle(self, *args, **options):

        fixture_dir = os.path.join(settings.BASE_DIR, 'tests/fixtures')

        def grouper(m):
            return self.model_name(m).rsplit('.', 1)[1]

        models = sorted(apps.get_models(), key=grouper)

        sources = set()

        for base_model, all_models in itertools.groupby(models, key=grouper):
            if base_model in options['apps']:
                base_model = list(all_models)[0]
                base_model_name = self.model_name(base_model)

                app_name = base_model_name.split('.', 1)[0]

                related = ['{0}.{1}'.format(base_model_name, r)
                           for r in dir(base_model)
                           if r.startswith(app_name) and r.endswith('_set')]

                output = StringIO()
                if related:
                    call_command('makefixture', '{}[:10]'.format(base_model_name),
                                 reverse=','.join(related),
                                 stdout=output)
                else:
                    call_command('makefixture', '{}[:10]'.format(base_model_name),
                                 stdout=output)
                output.seek(0)

                fixtures = json.load(output)

                for obj in fixtures:
                    if obj['fields'].get('sources'):
                        for source in obj['fields']['sources']:
                            sources.add(source)

                with open(os.path.join(fixture_dir, '{}.json'.format(app_name)), 'w') as f:
                    json.dump(fixtures, f)

        sources = Source.objects.filter(uuid__in=sources)
        accesspoints = AccessPoint.objects.filter(source__uuid__in=sources)

        source_fixture = serializers.serialize('json', sources)
        accesspoint_fixture = serializers.serialize('json', accesspoints)

        with open(os.path.join(fixture_dir, 'source.json'), 'w') as f:
            f.write(source_fixture)

        with open(os.path.join(fixture_dir, 'accesspoint.json'), 'w') as f:
            f.write(accesspoint_fixture)



        # 'tests/fixtures/auth.json',
        # 'tests/fixtures/source.json',
        # 'tests/fixtures/accesspoint.json',
        # 'tests/fixtures/organization.json',
        # 'tests/fixtures/person.json',
        # 'tests/fixtures/violation.json',
        # 'tests/fixtures/membershiporganization.json',
        # 'tests/fixtures/membershipperson.json',
