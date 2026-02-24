from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
import uuid

def custom_upload(instance, filename):
    ext = filename.split('.')[-1]
    new_name = f"{uuid.uuid4()}.{ext}"
    return f"uploads/avatars/{new_name}"

class User(AbstractUser):
    """Extended user model with additional profile fields"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    avatar = models.ImageField(upload_to=custom_upload, blank=True, null=True)

    # Preferences
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    marketing_emails = models.BooleanField(default=False)
    
    # Security
    mfa_enabled = models.BooleanField(default=False)
    mfa_method = models.CharField(
        max_length=20,
        choices=[
            # ('authenticator', 'Authenticator App'),
            ('sms', 'SMS'),
            ('email', 'Email'),
        ],
        blank=True,
        null=True
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return self.email
