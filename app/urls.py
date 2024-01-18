"""
URL configuration for app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from main import views
from quotes.views import contract_detail_view, contract_list_view, exchange_list_view, instrument_list_view, load_data_view, price_data_view


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('quote_load/', load_data_view, name='load_data_view'),
    path('exchanges/', exchange_list_view, name='exchange_list_view'),
    path('exchanges/<str:exchange>/', instrument_list_view, name='instrument_list_view'),
    path('exchanges/<str:exchange>/<str:instrument>/', contract_list_view, name='contract_list_view'),
    path('exchanges/<str:exchange>/<str:instrument>/<str:contract>/', contract_detail_view, name='contract_detail_view'),
    path('price_data/', price_data_view, name='price_data'),
]
