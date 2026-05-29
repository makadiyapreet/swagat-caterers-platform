"""
Section 10: Update Menu Item Stats
Counts how many events each menu item appears in.
Usage: python manage.py update_menu_stats
"""
from django.core.management.base import BaseCommand
from catering.models import Menu_item, MenuItemStats, CateringEvent
from django.db.models import Count


class Command(BaseCommand):
    help = 'Update menu item statistics (booking count, seasonal peak)'

    def handle(self, *args, **options):
        items = Menu_item.objects.all()
        updated = 0

        for item in items:
            # Count events that include this item
            booking_count = item.events.count()

            # Find peak months
            month_counts = (
                item.events
                    .values('date__month')
                    .annotate(count=Count('id'))
                    .order_by('-count')
            )
            peak_months = ','.join(str(m['date__month']) for m in month_counts[:3])

            # Update or create stats
            stats, created = MenuItemStats.objects.update_or_create(
                menu_item=item,
                defaults={
                    'booking_count': booking_count,
                    'seasonal_peak': peak_months,
                }
            )
            updated += 1

        self.stdout.write(self.style.SUCCESS(f'Updated stats for {updated} menu items'))
