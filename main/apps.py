from django.apps import AppConfig
from django.dispatch import Signal
from .utilities import send_activn


class MainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'
    verbose_name = 'Сервис обьявлений'

regsd_user = Signal()
def user_registered_dispatcher(sender, **kwargs):
        send_activn(kwargs['instance'])
regsd_user.connect(user_registered_dispatcher)


