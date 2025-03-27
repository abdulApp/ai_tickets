from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, TicketViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'tickets', TicketViewSet, basename='ticket')

urlpatterns = [
    path('', include(router.urls)),
]