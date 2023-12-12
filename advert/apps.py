from django.apps import AppConfig


class AdvertConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'advert'

    def ready(self):
        import advert.signals
