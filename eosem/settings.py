from pathlib import Path
import os
import dj_database_url  # Importante para conectar la BD de Render

# 1. RUTAS BASE
BASE_DIR = Path(__file__).resolve().parent.parent

# 2. SEGURIDAD (Configuración adaptada para producción)
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-g%y#^(y3zyfu6z-22gj!89a$*t*ufbi7%03s3z8=h)2=uh=eq0')

# Si existe la variable en Render, usa su valor (True/False); si no, por defecto es True localmente
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

# Permitir todos los hosts en Render para evitar bloqueos
ALLOWED_HOSTS = ['*']

# 3. APLICACIONES
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'dashboard',  # Tu aplicación principal
]

# 4. MIDDLEWARE (Se añade WhiteNoise justo debajo de SecurityMiddleware)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # <-- CLAVE PARA LOS ESTILOS EN RENDER
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'eosem.urls'

# 5. TEMPLATES (Configurado para tu carpeta dashboard/templates)
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "dashboard" / "templates"], 
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'eosem.wsgi.application'

# 6. BASE DE DATOS (Híbrida: Local vs Render)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'eosem_db',         
        'USER': 'postgres',        
        'PASSWORD': 'r123', 
        'HOST': 'localhost',         
        'PORT': '5432',              
    }
}

# Si estamos en Render, esta función reemplaza la configuración local por la de la nube automáticamente
if os.environ.get('DATABASE_URL'):
    DATABASES['default'] = dj_database_url.config(conn_max_age=600, ssl_require=True)

# 7. VALIDACIÓN DE CONTRASEÑAS
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# 8. INTERNACIONALIZACIÓN (Configurado para Colombia)
LANGUAGE_CODE = 'es-co'
TIME_ZONE = 'America/Bogota'
USE_I18N = True
USE_TZ = True

# 9. ARCHIVOS ESTÁTICOS (Imágenes, CSS, JS)
STATIC_URL = 'static/'

# Directorio de desarrollo
STATICFILES_DIRS = [
    BASE_DIR / "dashboard" / "static",
]

# Carpeta de producción (Donde 'collectstatic' guardará los archivos compilados)
STATIC_ROOT = BASE_DIR / 'staticfiles'  # <-- SOLUCIÓN AL ERROR DE RENDER

# 10. OTROS
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Configuración de Redirección de Login
LOGIN_URL = '/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/'
