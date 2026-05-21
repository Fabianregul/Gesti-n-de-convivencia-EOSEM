import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eosem.settings')
django.setup()

from django.contrib.auth.models import User

# Configura tus datos aquí
username = 'fabian_yusti'
email = 'yustif30@gmail.com'
password = 'cc1992'

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print("¡Superusuario creado con éxito automáticamente!")
else:
    print("El superusuario ya existe.")