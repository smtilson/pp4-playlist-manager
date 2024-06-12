from django.apps import AppConfig
# change this once I know which thing to import
# from django.core.signals import *


class ProfilesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'profiles'

    def ready(self):
        from . import signals
# this is there example of connecting a signal handler
#request_finished.connect(signals.my_callback)