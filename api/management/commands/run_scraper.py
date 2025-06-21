import os
import subprocess
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Run the Scrapy spider to collect clothing data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--async',
            action='store_true',
            help='Run scraper in background',
        )
        parser.add_argument(
            '--timeout',
            type=int,
            default=300,
            help='Timeout in seconds (default: 300)',
        )

    def handle(self, *args, **options):
        self.stdout.write("🕷️ Starting scraper...")
        
        try:
            scraper_dir = os.path.join(settings.BASE_DIR, 'scraper', 'vistet_scraper', 'vistet_scraper')
            
            if not os.path.exists(scraper_dir):
                self.stdout.write(
                    self.style.ERROR(f"❌ Scraper directory not found: {scraper_dir}")
                )
                return
            
            # Run the spider
            result = subprocess.run(
                ['scrapy', 'crawl', 'details_spider'],
                cwd=scraper_dir,
                capture_output=True,
                text=True,
                timeout=options['timeout']
            )
            
            if result.returncode == 0:
                self.stdout.write(
                    self.style.SUCCESS("✅ Scraper completed successfully!")
                )
                # Show some output but not too much
                output_lines = result.stdout.split('\n')
                for line in output_lines:
                    if any(keyword in line.lower() for keyword in ['saved', 'created', 'updated', 'error', 'warning']):
                        self.stdout.write(f"📊 {line}")
            else:
                self.stdout.write(
                    self.style.ERROR(f"❌ Scraper failed with return code {result.returncode}")
                )
                self.stdout.write(f"Error output: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            self.stdout.write(
                self.style.WARNING(f"⏰ Scraper timed out after {options['timeout']} seconds")
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Error running scraper: {e}")
            ) 