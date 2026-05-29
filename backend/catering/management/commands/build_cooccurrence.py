"""
Section 11: Build Co-Occurrence Matrix
Analyzes which menu items are frequently ordered together.
Usage: python manage.py build_cooccurrence
"""
from django.core.management.base import BaseCommand
from catering.models import Menu_item, ItemCoOccurrence, CateringEvent
from itertools import combinations


class Command(BaseCommand):
    help = 'Build item co-occurrence matrix from event menu selections'

    def handle(self, *args, **options):
        # Clear old data
        ItemCoOccurrence.objects.all().delete()

        events = CateringEvent.objects.prefetch_related('menu_items').all()
        pair_counts = {}

        for event in events:
            items = list(event.menu_items.all())
            if len(items) < 2:
                continue

            # Generate all pairs
            for item_a, item_b in combinations(items, 2):
                # Ensure consistent ordering (smaller ID first)
                if item_a.id > item_b.id:
                    item_a, item_b = item_b, item_a

                key = (item_a.id, item_b.id)
                pair_counts[key] = pair_counts.get(key, 0) + 1

        # Bulk create
        created = 0
        for (a_id, b_id), count in pair_counts.items():
            ItemCoOccurrence.objects.create(
                item_a_id=a_id,
                item_b_id=b_id,
                count=count
            )
            created += 1

        self.stdout.write(
            self.style.SUCCESS(f'Built {created} co-occurrence pairs from {events.count()} events')
        )
