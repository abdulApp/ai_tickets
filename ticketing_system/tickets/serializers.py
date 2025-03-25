from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Ticket

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'user_type')  # Include the fields you need
        read_only_fields = ('id',)  # id should not be modified

class TicketSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)  # Use the UserSerializer for nested representation
    assigned_to = UserSerializer(read_only=True, allow_null=True)

    class Meta:
        model = Ticket
        fields = ('id', 'title', 'description', 'status', 'created_by', 'assigned_to', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at', 'created_by')  # These fields should not be modified during create/update