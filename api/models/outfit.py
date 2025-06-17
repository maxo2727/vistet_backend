from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Outfit(models.Model):
    """
    Outfit model representing a combination of clothing items
    Users can create outfits mixing their personal clothes with store items
    """
    user = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='outfits'
    )
    name = models.CharField(max_length=100)
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5"
    )
    
    # Many-to-many relationship with Clothe for better scalability
    # Using string reference to avoid circular imports
    components = models.ManyToManyField(
        'Clothe',
        related_name='outfits',
        help_text="Clothing items that make up this outfit"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} by {self.user.name}" 