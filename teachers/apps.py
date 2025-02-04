# teachers/apps.py
from django.apps import AppConfig

class TeachersConfig(AppConfig):
    name = 'teachers'

    def ready(self):
        # Import the signals module to register signal handlers.
        import teachers.signals
