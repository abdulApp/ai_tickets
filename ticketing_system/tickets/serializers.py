from rest_framework import viewsets, serializers
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from .models import Ticket

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'first_name', 'last_name', 'user_type')  # Include the fields you need
        read_only_fields = ('id',)  # id should not be modified

class TicketSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)  # Use the UserSerializer for nested representation
    assigned_to = UserSerializer(read_only=True, allow_null=True)

    class Meta:
        model = Ticket
        fields = '__all__'  # Include all fields
        read_only_fields = ('id', 'created_at', 'updated_at', 'created_by')  # These fields should not be modified during create/update