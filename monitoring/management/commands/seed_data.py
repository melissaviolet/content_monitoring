"""
Custom Django management command to load test data.

Run it with:
    python manage.py seed_data

This creates:
- 8 keywords
- 8 articles
- runs the scanner to generate flags
- marks a couple of flags as relevant/irrelevant
  so your dashboard and flags page have a realistic mix to show
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from monitoring.models import Keyword, ContentItem, Flag
from monitoring.services.scanner import run_scan
from monitoring.services.content_loader import load_mock_data


class Command(BaseCommand):
    # This text shows when you run `python manage.py help seed_data`
    help = 'Seeds the database with test keywords, articles, and flags'

    def handle(self, *args, **options):
        # ── Step 1: Clear existing data ──
        # so running this command twice doesn't create duplicates
        self.stdout.write('Clearing existing data...')
        Flag.objects.all().delete()
        ContentItem.objects.all().delete()
        Keyword.objects.all().delete()

        # ── Step 2: Create keywords ──
        self.stdout.write('Creating keywords...')
        keyword_names = [
            'AI', 'election', 'climate', 'vaccine',
            'Django', 'Python', 'crypto', 'social media'
        ]
        for name in keyword_names:
            Keyword.objects.create(name=name)
        self.stdout.write(self.style.SUCCESS(f'  Created {len(keyword_names)} keywords'))

        # ── Step 3: Create articles ──
        # This calls the SAME function the "Import Content" button uses.
        # That way there's only one place articles are defined: content_loader.py
        self.stdout.write('Creating articles...')
        load_mock_data()
        article_count = ContentItem.objects.count()
        self.stdout.write(self.style.SUCCESS(f'  Created {article_count} articles'))

        # ── Step 4: Run the scanner to generate flags ──
        self.stdout.write('Running scanner...')
        run_scan()
        flag_count = Flag.objects.count()
        self.stdout.write(self.style.SUCCESS(f'  Generated {flag_count} flags'))

        # ── Step 5: Mark a few flags as reviewed ──
        # so the dashboard shows a realistic mix instead of everything "pending"
        self.stdout.write('Marking some flags as reviewed...')

        all_flags = list(Flag.objects.all())

        # Mark the first 3 flags as 'relevant'
        for flag in all_flags[:3]:
            flag.status = 'relevant'
            flag.reviewed_at = timezone.now()
            flag.save()

        # Mark the next 2 flags as 'irrelevant'
        for flag in all_flags[3:5]:
            flag.status = 'irrelevant'
            flag.reviewed_at = timezone.now()
            flag.save()

        self.stdout.write(self.style.SUCCESS('  Marked 3 relevant, 2 irrelevant'))

        # ── Done ──
        self.stdout.write(self.style.SUCCESS('\n✓ Database seeded successfully!'))
        self.stdout.write(f'  Keywords: {Keyword.objects.count()}')
        self.stdout.write(f'  Articles: {ContentItem.objects.count()}')
        self.stdout.write(f'  Flags:    {Flag.objects.count()}')
        self.stdout.write(f'    - Pending:    {Flag.objects.filter(status="pending").count()}')
        self.stdout.write(f'    - Relevant:   {Flag.objects.filter(status="relevant").count()}')
        self.stdout.write(f'    - Irrelevant: {Flag.objects.filter(status="irrelevant").count()}')