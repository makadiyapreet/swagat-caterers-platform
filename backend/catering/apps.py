from django.apps import AppConfig

class CateringConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'catering'

    def ready(self):
        # This turns on the signals. Without this, NO emails will send.
        import catering.signals