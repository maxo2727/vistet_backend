from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.http import HttpResponse
from django.urls import reverse
from django.utils.html import format_html

from .models import Clothe, Comment, Outfit, Store, User

"""
EXPLANATION OF ADMIN FEATURES:
- list_display: Columns shown in the main admin list
- list_filter: Sidebar filters for easy data filtering
- search_fields: Fields that can be searched with the search box
- ordering: Default ordering of records
- fieldsets: Groups fields in the edit form for better organization
- add_fieldsets: Special fieldsets for adding new users
- readonly_fields: These fields can't be edited (auto-generated timestamps)
- get_owner: Custom method to display who owns the clothing item
- filter_horizontal: Creates a nice interface for many-to-many relationships
- get_components_count: Shows how many clothing items are in the outfit
"""


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """
    Custom User admin configuration
    """

    list_display = ("name", "email", "description", "date_joined")
    list_filter = ("date_joined", "is_staff", "is_active")
    search_fields = ("name", "email")
    readonly_fields = ("date_joined", "last_login")


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    """
    Store admin configuration
    """

    list_display = ("name", "contact_number", "site_url", "created_at")
    list_filter = ("created_at",)
    search_fields = ("name", "description")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Clothe)
class ClotheAdmin(admin.ModelAdmin):
    """
    Clothe admin configuration
    """

    list_display = (
        "name",
        "type",
        "vendor",
        "base_price",
        "user",
        "store",
        "shopify_id",
        "created_at",
    )
    list_filter = ("type", "vendor", "created_at", "store", "user")
    search_fields = ("name", "vendor", "gid")
    readonly_fields = (
        "created_at",
        "updated_at",
        "price_range_display",
        "available_sizes_display",
    )

    def price_range_display(self, obj):
        min_price, max_price = obj.get_price_range()
        if min_price == max_price:
            return f"${min_price:,.0f} CLP"
        return f"${min_price:,.0f} - ${max_price:,.0f} CLP"

    price_range_display.short_description = "Price Range"

    def available_sizes_display(self, obj):
        sizes = obj.get_available_sizes()
        return ", ".join(sizes) if sizes else "No sizes"

    available_sizes_display.short_description = "Available Sizes"


@admin.register(Outfit)
class OutfitAdmin(admin.ModelAdmin):
    """
    Outfit admin configuration
    """

    list_display = ("name", "user", "rating", "created_at")
    list_filter = ("rating", "created_at")
    search_fields = ("name", "user__name")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """
    Comment admin configuration
    """

    list_display = ("user", "outfit", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__name", "content")
    readonly_fields = ("created_at", "updated_at")


# Custom admin view for API Documentation
class APIDocumentationAdmin:
    def get_urls(self):
        from django.urls import path

        return [
            path("api-docs/", self.api_documentation_view, name="api-docs"),
        ]

    def api_documentation_view(self, request):
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>VisteT API Documentation</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .endpoint { background: #f5f5f5; padding: 15px; margin: 10px 0; border-left: 4px solid #007cba; }
                .method { font-weight: bold; color: #007cba; }
                .url { font-family: monospace; background: #e8e8e8; padding: 2px 5px; }
                .description { margin: 8px 0; }
                .example { background: #f0f0f0; padding: 10px; border-radius: 4px; font-family: monospace; }
                h1 { color: #333; }
                h2 { color: #007cba; border-bottom: 2px solid #007cba; padding-bottom: 5px; }
            </style>
        </head>
        <body>
            <h1>🎯 VisteT API Documentation</h1>
            <p>Complete API reference for the VisteT clothing management system.</p>

            <h2>👕 Clothe Endpoints</h2>

            <div class="endpoint">
                <div class="method">GET</div>
                <div class="url">/api/clothe/all/</div>
                <div class="description">Get all clothing items with pagination (20 items per page)</div>
                <div class="example">curl http://localhost:8000/api/clothe/all/</div>
            </div>

            <div class="endpoint">
                <div class="method">POST</div>
                <div class="url">/api/clothe/</div>
                <div class="description">Create a new clothing item manually</div>
                <div class="example">curl -X POST http://localhost:8000/api/clothe/ -H "Content-Type: application/json" -d '{"name": "Cool Shirt", "type": "SHIRT", "image": "http://example.com/image.jpg"}'</div>
            </div>

            <div class="endpoint">
                <div class="method">GET</div>
                <div class="url">/api/clothe/{id}/</div>
                <div class="description">Get specific clothing item by ID</div>
                <div class="example">curl http://localhost:8000/api/clothe/1/</div>
            </div>

            <div class="endpoint">
                <div class="method">PUT</div>
                <div class="url">/api/clothe/{id}/</div>
                <div class="description">Update specific clothing item</div>
                <div class="example">curl -X PUT http://localhost:8000/api/clothe/1/ -H "Content-Type: application/json" -d '{"name": "Updated Name"}'</div>
            </div>

            <div class="endpoint">
                <div class="method">DELETE</div>
                <div class="url">/api/clothe/{id}/</div>
                <div class="description">Delete specific clothing item</div>
                <div class="example">curl -X DELETE http://localhost:8000/api/clothe/1/</div>
            </div>

            <div class="endpoint">
                <div class="method">POST</div>
                <div class="url">/api/clothe/from-scraped/</div>
                <div class="description">Create clothing item from scraped Shopify data</div>
                <div class="example">curl -X POST http://localhost:8000/api/clothe/from-scraped/ -H "Content-Type: application/json" -d '{"id": 123, "gid": "gid://shopify/Product/123", "vendor": "Brand", "type": "Shorts", "title": "Product Name", "variants": [...]}'</div>
            </div>

            <div class="endpoint">
                <div class="method">POST</div>
                <div class="url">/api/clothe/bulk-from-scraped/</div>
                <div class="description">Bulk create clothing items from scraped data</div>
                <div class="example">curl -X POST http://localhost:8000/api/clothe/bulk-from-scraped/ -H "Content-Type: application/json" -d '{"products": [...]}'</div>
            </div>

            <div class="endpoint">
                <div class="method">GET</div>
                <div class="url">/api/clothe/stats/</div>
                <div class="description">Get database statistics (total items, by type, by vendor)</div>
                <div class="example">curl http://localhost:8000/api/clothe/stats/</div>
            </div>

            <h2>🔍 Query Parameters</h2>
            <div class="endpoint">
                <div class="description">Filter clothing items by type or vendor:</div>
                <div class="example">GET /api/clothe/all/?type=SHORTS&vendor=REHAB</div>
            </div>

            <h2>📊 Response Format</h2>
            <div class="endpoint">
                <div class="description">All clothing items include computed fields:</div>
                <div class="example">{
  "id": 1,
  "name": "Jorts Ultra Baggy Black",
  "type": "SHORTS",
  "vendor": "REHAB CLO.",
  "base_price": "37990.00",
  "variants": [...],
  "price_range": {"price": 37990.0},
  "available_sizes": ["S/28US", "M/31US", "L/34US"]
}</div>
            </div>

            <h2>🕷️ Scraper Integration</h2>
            <p>The spider automatically runs and saves data to these endpoints:</p>
            <div class="endpoint">
                <div class="description">Run scraper manually:</div>
                <div class="example">cd vistet_backend/scraper/vistet_scraper && scrapy crawl details_spider</div>
            </div>
        </body>
        </html>
        """
        return HttpResponse(html)


# Note: To add custom admin views, you need to modify the main urls.py file
# The APIDocumentationAdmin class above can be used in a custom admin view implementation
