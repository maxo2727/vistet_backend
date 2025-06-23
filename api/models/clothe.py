import json

from django.db import models


class Clothe(models.Model):
    """
    Clothing item model - can belong to either a user or a store
    This is the core entity that represents individual pieces of clothing in VisteT
    """

    # Clothing type choices (enum-like behavior)
    class ClothingType(models.TextChoices):
        SHIRT = "SHIRT", "Shirt"
        PANTS = "PANTS", "Pants"
        DRESS = "DRESS", "Dress"
        SHOES = "SHOES", "Shoes"
        JACKET = "JACKET", "Jacket"
        SWEATER = "SWEATER", "Sweater"
        SHORTS = "SHORTS", "Shorts"
        SKIRT = "SKIRT", "Skirt"
        BLOUSE = "BLOUSE", "Blouse"
        HOODIE = "HOODIE", "Hoodie"
        COAT = "COAT", "Coat"
        JEANS = "JEANS", "Jeans"
        ACCESSORIES = "ACCESSORIES", "Accessories"
        POLERA = "POLERA", "Polera"
        OTHER = "OTHER", "Other"

    name = models.CharField(max_length=100)
    type = models.CharField(
        max_length=20, choices=ClothingType.choices, default=ClothingType.OTHER
    )
    image = models.ImageField(
        upload_to='clothes/images/', 
        null=True, 
        blank=True,
        help_text="Upload clothing image file"
    )
    image_url = models.URLField(
        null=True, 
        blank=True, 
        help_text="External image URL (for scraped items)"
    )

    # Scraped/external store data
    shopify_id = models.BigIntegerField(
        null=True, blank=True, unique=True, help_text="Shopify product ID"
    )
    gid = models.CharField(
        max_length=200, null=True, blank=True, help_text="Shopify Global ID"
    )
    vendor = models.CharField(
        max_length=100, null=True, blank=True, help_text="Product vendor/brand"
    )
    base_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Base price in CLP",
    )

    # Variants stored as JSON for flexibility and performance
    variants = models.JSONField(
        default=list,
        blank=True,
        help_text="Product variants with size, price, SKU info",
    )

    # Foreign keys - a clothe can belong to either a user OR a store
    # Import moved to avoid circular imports
    user = models.ForeignKey(
        "User", on_delete=models.CASCADE, null=True, blank=True, related_name="clothes"
    )
    store = models.ForeignKey(
        "Store", on_delete=models.CASCADE, null=True, blank=True, related_name="clothes"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(user__isnull=False, store__isnull=True)
                    | models.Q(user__isnull=True, store__isnull=False)
                ),
                name="clothe_belongs_to_user_or_store",
            )
        ]
        indexes = [
            models.Index(fields=["shopify_id"]),
            models.Index(fields=["vendor"]),
            models.Index(fields=["type"]),
        ]

    def __str__(self):
        if self.user:
            owner = self.user.name
        elif self.store:
            owner = self.store.name
        else:
            owner = "No owner"
        return f"{self.name} ({self.type}) - {owner}"

    def get_price_range(self):
        """Get min and max price from variants"""
        if not self.variants:
            return self.base_price, self.base_price

        prices = [
            variant.get("price", 0) for variant in self.variants if variant.get("price")
        ]
        if not prices:
            return self.base_price, self.base_price

        # Convert from centavos to pesos (Shopify stores prices in centavos)
        min_price = min(prices) / 100
        max_price = max(prices) / 100
        return min_price, max_price

    def get_available_sizes(self):
        """Get list of available sizes from variants"""
        return [
            variant.get("public_title", "")
            for variant in self.variants
            if variant.get("public_title")
        ]

    def get_image_url(self):
        """Get image URL - prioritize uploaded file over external URL"""
        if self.image and hasattr(self.image, 'url'):
            image_path = str(self.image)
            if not image_path.startswith(('http://', 'https://')):
                return self.image.url
        return self.image_url
