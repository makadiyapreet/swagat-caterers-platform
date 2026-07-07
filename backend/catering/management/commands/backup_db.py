"""
Database Backup Management Command
Usage:
    python manage.py backup_db              # Create a backup
    python manage.py backup_db --list       # List existing backups
    python manage.py backup_db --clean 30   # Delete backups older than 30 days
    
Cron example (daily at 2 AM):
    0 2 * * * cd /path/to/backend && source venv/bin/activate && python manage.py backup_db
"""
import os
import subprocess
import datetime
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings


class Command(BaseCommand):
    help = 'Create a database backup (SQLite or PostgreSQL)'

    def add_arguments(self, parser):
        parser.add_argument('--list', action='store_true', help='List existing backups')
        parser.add_argument('--clean', type=int, metavar='DAYS', help='Delete backups older than N days')

    def handle(self, *args, **options):
        backup_dir = Path(settings.BASE_DIR) / 'backups'
        backup_dir.mkdir(exist_ok=True)

        if options['list']:
            self._list_backups(backup_dir)
            return

        if options['clean']:
            self._clean_old(backup_dir, options['clean'])
            return

        # Create backup
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        db_settings = settings.DATABASES['default']
        engine = db_settings.get('ENGINE', '')

        if 'sqlite3' in engine:
            self._backup_sqlite(db_settings, backup_dir, timestamp)
        elif 'postgresql' in engine or 'postgis' in engine:
            self._backup_postgres(db_settings, backup_dir, timestamp)
        else:
            raise CommandError(f'Unsupported database engine: {engine}')

        # Email notification
        self._notify_admin(timestamp, backup_dir)

    def _backup_sqlite(self, db_settings, backup_dir, timestamp):
        import shutil
        db_path = db_settings['NAME']
        backup_file = backup_dir / f'swagat_db_{timestamp}.sqlite3'
        shutil.copy2(db_path, backup_file)
        size = backup_file.stat().st_size / (1024 * 1024)
        self.stdout.write(self.style.SUCCESS(
            f'✅ SQLite backup created: {backup_file.name} ({size:.1f} MB)'
        ))

    def _backup_postgres(self, db_settings, backup_dir, timestamp):
        backup_file = backup_dir / f'swagat_db_{timestamp}.sql.gz'
        
        env = os.environ.copy()
        if db_settings.get('PASSWORD'):
            env['PGPASSWORD'] = db_settings['PASSWORD']

        cmd = [
            'pg_dump',
            '-h', db_settings.get('HOST', 'localhost'),
            '-p', str(db_settings.get('PORT', '5432')),
            '-U', db_settings.get('USER', 'postgres'),
            '-d', db_settings.get('NAME', ''),
            '--no-owner',
            '--no-privileges',
        ]

        try:
            with open(backup_file, 'wb') as f:
                import gzip
                dump = subprocess.run(cmd, capture_output=True, env=env, check=True)
                with gzip.open(backup_file, 'wb') as gz:
                    gz.write(dump.stdout)
            
            size = backup_file.stat().st_size / (1024 * 1024)
            self.stdout.write(self.style.SUCCESS(
                f'✅ PostgreSQL backup created: {backup_file.name} ({size:.1f} MB)'
            ))
        except FileNotFoundError:
            raise CommandError('pg_dump not found. Install PostgreSQL client tools.')
        except subprocess.CalledProcessError as e:
            raise CommandError(f'pg_dump failed: {e.stderr.decode()}')

    def _list_backups(self, backup_dir):
        backups = sorted(backup_dir.glob('swagat_db_*'), key=lambda p: p.stat().st_mtime, reverse=True)
        if not backups:
            self.stdout.write(self.style.WARNING('No backups found.'))
            return
        
        self.stdout.write(self.style.SUCCESS(f'\n📁 {len(backups)} backup(s) in {backup_dir}:\n'))
        for b in backups:
            size = b.stat().st_size / (1024 * 1024)
            mtime = datetime.datetime.fromtimestamp(b.stat().st_mtime).strftime('%d-%b-%Y %H:%M')
            self.stdout.write(f'  {b.name:<45} {size:>6.1f} MB   {mtime}')

    def _clean_old(self, backup_dir, days):
        cutoff = datetime.datetime.now() - datetime.timedelta(days=days)
        removed = 0
        for b in backup_dir.glob('swagat_db_*'):
            mtime = datetime.datetime.fromtimestamp(b.stat().st_mtime)
            if mtime < cutoff:
                b.unlink()
                removed += 1
                self.stdout.write(f'  Deleted: {b.name}')
        self.stdout.write(self.style.SUCCESS(f'\n🗑️ Removed {removed} backup(s) older than {days} days.'))

    def _notify_admin(self, timestamp, backup_dir):
        try:
            from django.core.mail import send_mail
            admin_email = getattr(settings, 'ADMIN_ALERT_EMAIL', getattr(settings, 'ADMIN_EMAIL', ''))
            if not admin_email:
                return
            
            backups = list(backup_dir.glob('swagat_db_*'))
            total_size = sum(b.stat().st_size for b in backups) / (1024 * 1024)
            
            send_mail(
                subject=f'💾 Database Backup Completed — {timestamp}',
                message=(
                    f'Database backup completed successfully.\n\n'
                    f'Timestamp: {timestamp}\n'
                    f'Total backups: {len(backups)}\n'
                    f'Total size: {total_size:.1f} MB\n\n'
                    f'---\n'
                    f'Swagat Caterers — Automated Backup System\n'
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[admin_email],
                fail_silently=True,
            )
        except Exception:
            pass
