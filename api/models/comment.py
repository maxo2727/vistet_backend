from django.db import models


class Comment(models.Model):
    """
    Comment model for users to comment on outfits
    Enables social interaction and feedback on outfit creations
    """
    user = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='comments'
    )
    outfit = models.ForeignKey(
        'Outfit',
        on_delete=models.CASCADE,
        related_name='comments'
    )
    title = models.CharField(max_length=100)
    message = models.TextField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} by {self.user.name} on {self.outfit.name}" 