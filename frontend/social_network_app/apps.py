# social_network_app/apps.py

from django.apps import AppConfig

class SocialNetworkAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'social_network_app'

    def ready(self):
        import social_network_app.signals  # Import your signals here
