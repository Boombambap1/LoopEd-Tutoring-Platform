from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Create admin user if it doesn\'t exist'
    
    def handle(self, *args, **options):
        User = get_user_model()
        username = 'admin'
        email = 'loopedcollab@gmail.com'
        password = 'Boombambap1'  # Change this!
        
        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username, email, password)
            self.stdout.write(
                self.style.SUCCESS(f'Admin user "{username}" created successfully!')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'Admin user "{username}" already exists')
            )