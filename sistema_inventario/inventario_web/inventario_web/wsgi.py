"""
WSGI config for inventario_web project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from django.core.management import call_command

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventario_web.settings')

# Vercel Hack: Run migrations on startup to ensure SQLite is up to date
# This is necessary because the build step modification to db.sqlite3 might not persist to the lambda environment
try:
    print("Running migrations on startup...")
    call_command('migrate')
except Exception as e:
    print(f"Error running migrations: {e}")

application = get_wsgi_application()

app = application