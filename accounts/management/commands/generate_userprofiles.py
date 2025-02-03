# accounts/management/commands/generate_userprofiles.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import Profile

class Command(BaseCommand):
    help = "Generate user profiles for users missing a profile."

    def handle(self, *args, **options):
        users = User.objects.all()
        created_count = 0
        for user in users:
            profile, created = Profile.objects.get_or_create(user=user, defaults={'role': 'Student'})
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"Created profile for {user.username}"))
            else:
                self.stdout.write(f"Profile already exists for {user.username}")
        self.stdout.write(self.style.SUCCESS(f"Total profiles created: {created_count}"))
