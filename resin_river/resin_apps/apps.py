from django.apps import AppConfig


class ResinAppsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'resin_apps'
    
    def ready(self):
        import resin_apps.signals  # Import signals to register them