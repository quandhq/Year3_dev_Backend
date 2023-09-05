from django.apps import AppConfig

class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'
    ##
    #  @brief Websocket setup.
    #         The function "ready" will be called when the code is loaded. 
    def ready(self):     
        from api.signals import create_token #!< import api.signals and make it callable in ready function
    #________________________________________
