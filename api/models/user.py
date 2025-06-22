from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import RegexValidator
from django.db import models


class UserManager(BaseUserManager):
    """
    Custom user manager for email-based authentication
    """

    def create_user(self, email, name, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, name, password, **extra_fields)


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser
    Serves as the main user entity for VisteT app users
    """

    # Remove username field and use email as the unique identifier
    username = None
    email = models.EmailField(unique=True)

    # Custom fields
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    # Phone number validation for Chilean format +56 9 [8 numbers]
    phone_regex = RegexValidator(
        regex=r"^\+56\s9\s\d{4}\s\d{4}$",
        message="Phone number must be in format: +56 9 XXXX XXXX",
    )

    phone_regex_no_spaces = RegexValidator(
        regex=r"^\+569\d{8}$", message="Phone number must be in format: +569XXXXXXXX"
    )

    contact_number = models.CharField(
        validators=[phone_regex, phone_regex_no_spaces],
        max_length=17,
        blank=True,
        null=True,
        help_text="Format: +56 9 XXXX XXXX or +569XXXXXXXX",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    objects = UserManager()

    def __str__(self):
        return f"{self.name} ({self.email})"
