# celeryconfig.py
broker_transport_options = {'visibility_timeout': 3600}
imports = ('celery_app',)
