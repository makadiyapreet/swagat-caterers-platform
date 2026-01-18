from django.apps import AppConfig

class CateringConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'catering'

    def ready(self):
        import catering.signals # This loads the signals we just wrote