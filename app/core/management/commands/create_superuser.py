import os
from django.contrib.auth.models import User

def create_superuser():
    username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
    email = os.environ.get("DJANGO_SUPERUSER_EMAIL")
    password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")
    
    # Check if the user already exists
    if User.objects.filter(username=username).exists():
        print("Superuser already exists.")
        return
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f"Superuser {username} created.")

# Run the function to create a superuser
create_superuser()