from django.db import models


class Clothe(models.Model):
    """
    Clothing item model - can belong to either a user or a store
    This is the core entity that represents individual pieces of clothing in VisteT
    """
    
    # Clothing type choices (enum-like behavior)
    class ClothingType(models.TextChoices):
        SHIRT = 'SHIRT', 'Shirt'
        PANTS = 'PANTS', 'Pants'
        DRESS = 'DRESS', 'Dress'
        SHOES = 'SHOES', 'Shoes'
        JACKET = 'JACKET', 'Jacket'
        SWEATER = 'SWEATER', 'Sweater'
        SHORTS = 'SHORTS', 'Shorts'
        SKIRT = 'SKIRT', 'Skirt'
        BLOUSE = 'BLOUSE', 'Blouse'
        HOODIE = 'HOODIE', 'Hoodie'
        COAT = 'COAT', 'Coat'
        JEANS = 'JEANS', 'Jeans'
        ACCESSORIES = 'ACCESSORIES', 'Accessories'
        OTHER = 'OTHER', 'Other'
    
    name = models.CharField(max_length=100)
    type = models.CharField(
        max_length=20,
        choices=ClothingType.choices,
        default=ClothingType.OTHER
    )
    image = models.URLField(help_text="URL to the clothing image")
    
    # Foreign keys - a clothe can belong to either a user OR a store
    # Import moved to avoid circular imports
    user = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='clothes'
    )
    store = models.ForeignKey(
        'Store',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='clothes'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(user__isnull=False, store__isnull=True) |
                    models.Q(user__isnull=True, store__isnull=False)
                ),
                name='clothe_belongs_to_user_or_store'
            )
        ]
    
    def __str__(self):
        if self.user:
            owner = self.user.name
        elif self.store:
            owner = self.store.name
        else:
            owner = "No owner"
        return f"{self.name} ({self.type}) - {owner}" 