"""
production
~~~~~~~~~~

Run production server
"""
from meg.app import create_app


application, _, _, celery = create_app()
