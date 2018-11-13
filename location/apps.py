from django.apps import AppConfig


class LocationConfig(AppConfig):
    name = 'location'

    def ready(self):
        from location import signals
