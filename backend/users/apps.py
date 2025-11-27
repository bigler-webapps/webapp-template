from django.apps import AppConfig

class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
    # Die ready() Methode kann hier leer bleiben oder wegfallen, 
    # sofern du keine weiteren lokalen Signale in signals.py hast.