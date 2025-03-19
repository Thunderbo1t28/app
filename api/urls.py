from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.orders import OrderViewSet
from .views import (
    ArcticCapitalViewSet,
    InstrumentViewSet,
    TaskViewSet,
    check_task_status,
    instruments_status,
    load_history,
    load_to_database,
    run_systems,
)
from .views.auth import get_current_user
from .views.register import RegisterView
from .views.system import SystemViewSet
from .views.optimal_positions import OptimalPositionsListAPIView

router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='orders')
router.register(r'arctic-capital', ArcticCapitalViewSet)
router.register(r'instruments', InstrumentViewSet)
router.register(r'tasks', TaskViewSet, basename='tasks')
router.register(r'system', SystemViewSet, basename='system')

urlpatterns = [
    path('optimal-positions/', OptimalPositionsListAPIView.as_view(), name='optimal_positions'),
    path('tasks/<str:task_id>/status/', check_task_status, name='check_task_status'),
    path('tasks/instruments_status/', instruments_status, name='instruments_status'),
    path('tasks/load_history/', load_history, name='load_history'),
    path('tasks/load_to_database/', load_to_database, name='load_to_database'),
    path('tasks/run_systems/', run_systems, name='run_systems'),
    path('auth/me/', get_current_user, name='current-user'),
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('', include(router.urls)),
] 
