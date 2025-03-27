# # from django.shortcuts import render
# from rest_framework.decorators import api_view
# from rest_framework.response import Response

# # Create your views here.

from rest_framework import viewsets, permissions, serializers, status
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from rest_framework.decorators import action, api_view
from .models import Ticket
from .serializers import UserSerializer, TicketSerializer
import logging  # Import the logging module

@api_view(['GET'])
def hello_world(request):
    return Response({"message": "Ticketing System API is live!"})

User = get_user_model()
logger = logging.getLogger(__name__)  # Get a logger instance


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'first_name', 'last_name')

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()

        if validated_data.get('user_type') == 'engineer':
            engineer_group, created = Group.objects.get_or_create(name='Engineers')
            user.groups.add(engineer_group)
        elif validated_data.get('user_type') == 'admin':
            admin_group, created = Group.objects.get_or_create(name='Admins')
            user.groups.add(admin_group)
        # else:
        #     regular_group, created = Group.objects.get_or_create(name='Regulars')
        #     user.groups.add(regular_group)
        return user


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows users to be viewed.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = []  # All users can view, but must be authenticated

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        # Log the Authorization header
        logger.debug(f"Authorization header: {request.META.get('HTTP_AUTHORIZATION')}")
        return super().list(request, *args, **kwargs)

class TicketViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows tickets to be viewed and edited.
    """
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated] #all authenticated users can access.
    
    def get_queryset(self):
        """
        Filter tickets based on user type.
        - Regular users: only see their created tickets.
        - Engineers: only see assigned tickets.
        - Admins: see all tickets.
        """
        user = self.request.user
        if user.user_type == 'regular':
            return Ticket.objects.filter(created_by=user)
        elif user.user_type == 'eng':
            return Ticket.objects.filter(assigned_to=user)
        elif user.user_type == 'admin':
            return Ticket.objects.all()
        return Ticket.objects.none() #default

    def create(self, request, *args, **kwargs):
        """
        Regular users can create tickets.  Set created_by to the current user.
        """
        user = request.user
        if user.user_type == 'regular':
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(created_by=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({"detail": "Only regular users can create tickets."}, status=status.HTTP_403_FORBIDDEN)

    def update(self, request, *args, **kwargs):
        """
        Engineers can update the status of tickets assigned to them.
        Admins can update all fields.
        """
        user = request.user
        instance = self.get_object()
        if user.user_type == 'engineer':
            if instance.assigned_to == user:
                serializer = self.get_serializer(instance, data=request.data, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data)
            else:
                return Response({"detail": "You are not assigned to this ticket."}, status=status.HTTP_403_FORBIDDEN)
        elif user.user_type == 'admin':
             serializer = self.get_serializer(instance, data=request.data)
             serializer.is_valid(raise_exception=True)
             serializer.save()
             return Response(serializer.data)
        else:
            return Response({"detail": "You do not have permission to update this ticket."}, status=status.HTTP_403_FORBIDDEN)
        
    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """
        Admin can assign a ticket to an engineer.
        """
        user = request.user
        ticket = self.get_object()  # Get the ticket instance
        if user.user_type == 'admin':
            engineer_id = request.data.get('engineer_id')
            if engineer_id:
                try:
                    engineer = User.objects.get(id=engineer_id, user_type='engineer')
                    ticket.assigned_to = engineer
                    ticket.save()
                    serializer = self.get_serializer(ticket)
                    return Response(serializer.data)
                except User.DoesNotExist:
                    return Response({"detail": "Engineer with this ID not found."}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"detail": "engineer_id is required."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"detail": "Only admins can assign tickets."}, status=status.HTTP_403_FORBIDDEN)