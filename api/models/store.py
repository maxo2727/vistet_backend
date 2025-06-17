from django.db import models
from django.core.validators import RegexValidator


class Store(models.Model):
    """
    Store model for businesses that want to promote their products on VisteT
    Stores can upload clothing items that users can include in their outfits
    """
    name = models.CharField(max_length=100)
    description = models.TextField()
    
    # Using same phone validation as User for consistency
    phone_regex = RegexValidator(
        regex=r'^\+56\s9\s\d{4}\s\d{4}$',
        message="Phone number must be in format: +56 9 XXXX XXXX"
    )
    
    phone_regex_no_spaces = RegexValidator(
        regex=r'^\+569\d{8}$',
        message="Phone number must be in format: +569XXXXXXXX"
    )
    
    contact_number = models.CharField(
        validators=[phone_regex, phone_regex_no_spaces],
        max_length=17,
        help_text="Format: +56 9 XXXX XXXX or +569XXXXXXXX"
    )
    
    site_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name 