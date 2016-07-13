from django.apps import AppConfig

class SFMConfig(AppConfig):
    name = 'sfm_pc'
    def ready(self):
        from sfm_pc import signals
