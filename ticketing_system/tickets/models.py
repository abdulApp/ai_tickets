from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

# Create your models here.

class User(AbstractUser):
    """
    Custom User model to include user type.
    """
    USER_TYPE_CHOICES = (
        ('regular', 'Regular User'),
        ('admin', 'Admin'),
        ('engineer', 'Engineer'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='regular')

    def __str__(self):
        return self.username
    
class Ticket(models.Model):
    """
    Model for tickets.
    """
    STATUS_CHOICES = (
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='created_tickets', on_delete=models.CASCADE)
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='assigned_tickets', null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title