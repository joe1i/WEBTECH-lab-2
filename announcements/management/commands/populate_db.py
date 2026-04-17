import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from announcements.models import Announcement
from reactions.models import Reaction
from faker import Faker

User = get_user_model()
fake = Faker('uk_UA')


class Command(BaseCommand):
    help = 'Populate database with test data'

    def handle(self, *args, **options):
        self.stdout.write('Creating test data...')

        users = []
        for _ in range(15):
            gender = random.choice(['M', 'F', 'O'])
            user = User.objects.create_user(
                email=fake.unique.email(),
                username=fake.unique.user_name(),
                first_name=fake.first_name_male() if gender == 'M' else fake.first_name_female(),
                last_name=fake.last_name_male() if gender == 'M' else fake.last_name_female(),
                gender=gender,
                birth_date=fake.date_of_birth(minimum_age=18, maximum_age=60),
                bio=fake.text(max_nb_chars=200),
                password='testpassword123'
            )
            users.append(user)

        admin_user, created = User.objects.get_or_create(
            email='admin@example.com',
            defaults={
                'username': 'admin',
                'first_name': 'Головний',
                'last_name': 'Адмін',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin_user.set_password('adminpass123')
            admin_user.save()

        announcements = []
        for _ in range(10):
            announcement = Announcement.objects.create(
                title=fake.sentence(nb_words=5),
                content=fake.text(max_nb_chars=1000),
                author=admin_user,
                views_count=random.randint(10, 100)
            )
            announcements.append(announcement)

        reaction_types = ['like', 'heart', 'fire', 'sad']

        for announcement in announcements:
            reacting_users = random.sample(users, random.randint(3, 10))
            for user in reacting_users:
                Reaction.objects.create(
                    announcement=announcement,
                    user=user,
                    reaction_type=random.choice(reaction_types)
                )

        self.stdout.write(self.style.SUCCESS('Successfully created test data'))