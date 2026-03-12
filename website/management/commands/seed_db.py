from django.core.management.base import BaseCommand
from faker import Faker
from website.models import Website, Page
from django.contrib.auth.models import User
from django.core.files.base import ContentFile

fake = Faker()


class Command(BaseCommand):
    """Management command to seed the database with initial data for testing and development."""

    help = "Seed the database with initial data for testing and development."

    def handle(self, *args, **options):
        """Seed the database with sample users, websites, and pages."""

        for _ in range(5):
            # Create a test user
            user, created = User.objects.get_or_create(username=fake.user_name())
            if created:
                user.set_password("password123")
                user.save()

            # Create a test website
            website, created = Website.objects.get_or_create(
                user=user,
                name=fake.unique.domain_word(),
                description=fake.text(),
                url=fake.unique.url(),
            )
            if created:
                website.css.save(
                    "style.css", ContentFile("body { background-color: #f0f0f0; }")
                )
                website.js.save(
                    "script.js", ContentFile("console.log('Hello, world!');")
                )
                website.header.save(
                    "header.txt",
                    ContentFile("<header><h1>Welcome to Test Website</h1></header>"),
                )
                website.footer.save(
                    "footer.txt",
                    ContentFile("<footer><p>&copy; 2024 Test Website</p></footer>"),
                )
                website.save()

            # Create sample pages for the website
            for i in range(3):
                page, created = Page.objects.get_or_create(
                    website=website,
                    title=f"Page {i}",
                    slug=f"page-{i}",
                    meta_description=f"This is the meta description for Page {i}.",
                    meta_og_type="website",
                    meta_og_image=fake.image_url(),
                )
                if created:
                    page.content.save(
                        f"page-{i}-content.txt",
                        ContentFile(
                            f"<h2>This is Page {i}</h2><p>Content for page {i} goes here.</p>"
                        ),
                    )
                    page.save()

        self.stdout.write(self.style.SUCCESS("Database seeded successfully!"))
