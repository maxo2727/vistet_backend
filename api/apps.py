import os
import threading
import time
import subprocess
from django.apps import AppConfig
from django.conf import settings


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'
    verbose_name = 'VisteT API'

    def ready(self):
        """
        Called when Django starts up
        """
        # Only run scraper in the main process (not in reloader)
        if os.environ.get('RUN_MAIN') or not settings.DEBUG:
            # Run scraper in background thread to avoid blocking startup
            threading.Thread(target=self.run_initial_scraper, daemon=True).start()
    
    def run_initial_scraper(self):
        """
        Run the scraper once when the server starts
        """
        try:
            time.sleep(5)
            
            print("🕷️ Starting automatic scraper...")
            
            scraper_dir = os.path.join(settings.BASE_DIR, 'scraper', 'vistet_scraper', 'vistet_scraper')
            
            if os.path.exists(scraper_dir):
                result = subprocess.run(
                    ['scrapy', 'crawl', 'details_spider'],
                    cwd=scraper_dir,
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                
                if result.returncode == 0:
                    print("✅ Automatic scraper completed successfully!")
                    print(f"📊 Output: {result.stdout}")
                else:
                    print(f"❌ Scraper failed: {result.stderr}")
            else:
                print(f"❌ Scraper directory not found: {scraper_dir}")
                
        except subprocess.TimeoutExpired:
            print("⏰ Scraper timed out after 5 minutes")
        except Exception as e:
            print(f"❌ Error running automatic scraper: {e}")
