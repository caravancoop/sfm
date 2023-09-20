import csv
from datetime import datetime
import itertools
import os

from django.apps import apps
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand
from django.db import IntegrityError
from django.utils.text import slugify

from composition.models import Composition
from membershipperson.models import MembershipPerson
from source.models import Source, AccessPoint


class Command(BaseCommand):
    help = "Import sources from local file"

    def add_arguments(self, parser):
        parser.add_argument(
            "--sources_path", dest="sources_path", help="Path to the sources.csv file"
        )

    def disconnectSignals(self):
        from complex_fields.base_models import object_ref_saved
        from sfm_pc.signals import update_membership_index, update_composition_index

        object_ref_saved.disconnect(
            receiver=update_membership_index, sender=MembershipPerson
        )
        object_ref_saved.disconnect(
            receiver=update_composition_index, sender=Composition
        )

        apps.get_app_config("haystack").signal_processor.teardown()

    def connectSignals(self):
        from complex_fields.base_models import object_ref_saved
        from sfm_pc.signals import update_membership_index, update_composition_index

        object_ref_saved.connect(
            receiver=update_membership_index, sender=MembershipPerson
        )
        object_ref_saved.connect(receiver=update_composition_index, sender=Composition)

        apps.get_app_config("haystack").signal_processor.setup()

    def handle(self, *args, **options):
        self.disconnectSignals()

        importer_user = settings.IMPORTER_USER
        try:
            self.user = User.objects.create_user(
                importer_user["username"],
                email=importer_user["email"],
                password=importer_user["password"],
            )
        except IntegrityError:
            self.user = User.objects.get(username=importer_user["username"])

        self.create_sources(options["sources_path"])

        self.connectSignals()

    def get_records_from_csv(self, path):
        if not os.path.isfile(path):
            # Don't require a persons_extra file if it doesn't exist.
            if "persons_extra" in path:
                return []
            raise OSError("Required file {path} not found.".format(path=path))
        with open(path) as fobj:
            reader = csv.reader(fobj)
            # We could use csv.DictReader directly here, but instead use
            # the format_dict_reader convenience method to test it
            records = self.format_dict_reader(list(reader))

        return records

    def format_dict_reader(self, lst):
        """
        Format a nested list, 'lst', as a list of dictionaries (like a
        csv.DictReader object).
        """
        header = lst[0]
        # Use itertools.zip_longest to preserve all of the header fields. This
        # is important because if every cell after the ith column in a row is
        # empty, the API will truncate the row at the ith cell when it returns
        # a response, leading the built-in zip() function to leave out those
        # elements (zip() will default to the length of the shortest iterable).
        return [
            dict(itertools.zip_longest(header, row, fillvalue="")) for row in lst[1:]
        ]

    def get_source_date(self, date_value):
        """
        Source dates can come to us as full timestamps or dates. Given a string
        representing one of these values, return a parsed datetime or date
        object, or an empty string, if neither can be parsed.
        """
        try:
            # Try to parse the value as a timestamp (remove timezone marker for
            # Python <3.7)
            return datetime.strptime(date_value.replace("Z", ""), "%Y-%m-%dT%H:%M:%S")

        except ValueError:
            # Fall back to an empty string because we want to use this value to
            # retrieve and update existing Sources, and date fields default to
            # an empty string if no data is provided
            return self.parse_date(date_value) or ""

    def parse_date(self, value):
        parsed = None

        # Map legal input formats to the way that we want to
        # store them in the database
        formats = {
            "%Y-%m-%d": "%Y-%m-%d",
            "%Y": "%Y-0-0",
            "%Y-": "%Y-0-0",
            "%Y-%m": "%Y-%m-0",
            "%Y-%m-": "%Y-%m-0",
            "%B %Y": "%Y-%m-0",
            "%m/%Y": "%Y-%m-0",
            "%m/%d/%Y": "%Y-%m-%d",
        }

        for in_format, out_format in formats.items():
            try:
                parsed_input = datetime.strptime(value, in_format)

                if datetime.today() < parsed_input:
                    raise ValidationError(
                        "Date {value} is in the future".format(value=value)
                    )

                parsed = datetime.strftime(parsed_input, out_format)
                break
            except ValueError:
                pass

        return parsed

    def create_sources(self, sources_path):
        self.current_sheet = "sources"

        for idx, source_data in enumerate(self.get_records_from_csv(sources_path)):
            access_point_uuid = source_data["source:access_point_id:admin"].strip()

            try:
                access_point, _ = AccessPoint.objects.get_or_create(
                    uuid=access_point_uuid,
                    user=self.user,
                )

            except (ValidationError, ValueError):
                self.log_error(
                    'Invalid source UUID: "{}"'.format(access_point_uuid),
                    sheet="sources",
                    current_row=idx + 2,  # Handle 0-index and header row
                )
                continue

            source_info = {
                "title": source_data[Source.get_spreadsheet_field_name("title")],
                "type": source_data[Source.get_spreadsheet_field_name("type")],
                "author": source_data[Source.get_spreadsheet_field_name("author")],
                "publication": source_data[
                    Source.get_spreadsheet_field_name("publication")
                ],
                "publication_country": source_data[
                    Source.get_spreadsheet_field_name("publication_country")
                ],
                "source_url": source_data[
                    Source.get_spreadsheet_field_name("source_url")
                ],
                "user": self.user,
            }

            for prefix in ("published", "created", "uploaded"):
                date_value = source_data[
                    Source.get_spreadsheet_field_name("{}_date".format(prefix))
                ]

                try:
                    parsed_date = self.get_source_date(date_value)
                except ValidationError:
                    self.log_error(e.message, sheet="sources", row=idx + 2)
                    parsed_date = ""

                if isinstance(parsed_date, datetime):
                    source_info["{}_timestamp".format(prefix)] = parsed_date
                else:
                    source_info["{}_date".format(prefix)] = parsed_date

                if not parsed_date and prefix == "published":
                    message = 'Invalid published_date "{1}" at {2}'.format(
                        prefix, date_value, access_point_uuid
                    )
                    self.log_error(message, sheet="sources", current_row=idx + 2)

            source, created = Source.objects.get_or_create(**source_info)

            self.stdout.write(
                '{0} Source "{1}" from row {2}'.format(
                    "Created" if created else "Updated", source, idx + 2
                )
            )

            try:
                access_date = self.parse_date(
                    source_data[AccessPoint.get_spreadsheet_field_name("accessed_on")]
                )
            except ValidationError as e:
                self.log_error(e.message, sheet="sources", row=idx + 2)
                access_date = None

            access_point_info = {
                "type": source_data[AccessPoint.get_spreadsheet_field_name("type")],
                "trigger": source_data[
                    AccessPoint.get_spreadsheet_field_name("trigger")
                ],
                "accessed_on": access_date,
                "archive_url": source_data[
                    AccessPoint.get_spreadsheet_field_name("archive_url")
                ],
                "source": source,
                "user": self.user,
            }

            for attr, val in access_point_info.items():
                setattr(access_point, attr, val)

            access_point.save()

    def log_error(self, message, current_sheet, current_row):
        log_message = message + " (context: Sheet {0}, Row {1})".format(
            current_sheet, current_row
        )
        self.stdout.write(self.style.ERROR(log_message))
        file_name = "{}-errors.csv".format(slugify(current_sheet))

        if not os.path.isfile(file_name):
            with open(file_name, "w") as f:
                header = ["row", "message"]
                writer = csv.writer(f)
                writer.writerow(header)

        with open(file_name, "a") as f:
            writer = csv.writer(f)
            writer.writerow([current_row, message])
