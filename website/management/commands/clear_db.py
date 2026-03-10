from django.core.management.base import BaseCommand
from website.models import Website, Page
from django.contrib.auth.models import User

class Command(BaseCommand):
    '''Management command to clear all data from the database for testing and development.'''
    help = "Clear all data from the database for testing and development."

    def handle(self, *args, **options):
        '''Clear all data from the database, including users, websites, and pages.'''
        # Delete all pages
        Page.objects.all().delete()
        # Delete all websites
        Website.objects.all().delete()
        # delete all users 
        User.objects.all().delete()

        self.stdout.write(self.style.SUCCESS("Database cleared successfully!"))