from django.apps import AppConfig


class App2Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app2'
    
    def ready(self):
        import app2.signals
