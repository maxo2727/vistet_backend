from django.core.validators import RegexValidator
from django.db import models
from django.core.exceptions import ValidationError
import re

def validate_phone_number(value):
    pattern = r"^(?:\+56\s9\s\d{4}\s\d{4}|\+569\d{8})$"
    if not re.match(pattern, value):
        raise ValidationError("Invalid phone number. Must be in format: +56 9 XXXX XXXX or +569XXXXXXXX")

class Store(models.Model):
    """
    Store model for businesses that want to promote their products on VisteT
    Stores can upload clothing items that users can include in their outfits
    """

    name = models.CharField(max_length=100)
    description = models.TextField()

    contact_number = models.CharField(
        validators=[validate_phone_number],
        max_length=17,
        help_text="Format: +56 9 XXXX XXXX or +569XXXXXXXX",
    )

    site_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
