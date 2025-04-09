"""
WSGI config for bigAuth project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os
import logging
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bigAuth.settings')


# Configure logging before the application starts
logger = logging.getLogger('custom')
logger.info("Django server starting via WSGI")

application = get_wsgi_application()
