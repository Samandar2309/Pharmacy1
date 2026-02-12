from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'notifications'
    verbose_name = 'Bildirishnomalar'

    def ready(self):
        """Signallarni import qilish"""
        import notifications.signals
