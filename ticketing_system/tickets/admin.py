from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Ticket

# Register your models here.

class TicketAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'created_by', 'assigned_to', 'created_at')
    list_filter = ('status', 'assigned_to', 'created_by')
    search_fields = ('title', 'description')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)  # Sort by creation date, descending

# Register the User model with the custom UserAdmin
admin.site.register(User, UserAdmin)

# Register the Ticket model
admin.site.register(Ticket)