from tutoring_platform.settings import *
import os

# Production settings
DEBUG = False
ALLOWED_HOSTS = ['*.up.railway.app', 'looped.up.railway.app']

# Database - Railway provides PostgreSQL
import dj_database_url
DATABASES = {
    'default': dj_database_url.parse(os.environ.get('DATABASE_URL'))
}

# Static files
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files (user uploads) - THIS IS THE STEP 3 PART
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Security
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
