from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'contract_positions', contract_positionsViewSet)
router.register(r'arctic_capital', arctic_capitalViewSet)
router.register(r'instrument', instrumentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
