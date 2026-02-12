from django.apps import AppConfig


class PrescriptionsConfig(AppConfig):
    name = 'prescriptions'

    def ready(self):
        import prescriptions.signals
