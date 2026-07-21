from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegisterViewSet, me, VerificationRequestViewSet


router = DefaultRouter()
router.register(r'register', RegisterViewSet, basename='register')
router.register(r'verification-requests', VerificationRequestViewSet, basename='verification-requests')

urlpatterns = [
    path('', include(router.urls)),
    path('me/', me, name='me'),
]
