"""
production
~~~~~~~~~~

Run production server
"""
from meg.app import create_app


application, _ = create_app()
