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
from backtest.views import backtest_main, backtest_view, select_instruments_view, select_rules_view
from main import views
from quotes.views import (adjusted_prices_view, 
                          contract_detail_view, 
                          contract_list_view, create_instrument, data_view, 
                          exchange_list_view, fx_price_data_view, instrument_detail, 
                          instrument_list_view, 
                          load_data_view, 
                          multiple_price_data, 
                          roll_calendar, select_exchange_view, select_instrument_view, 
                          update_multiple_price_data)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('data/', data_view, name='data_view'),
    path('backtest/', backtest_main, name='backtest_main'),

    path('quote_load/', load_data_view, name='load_data_view'),
    path('exchanges/', exchange_list_view, name='exchange_list_view'),
    path('select_exchange/', select_exchange_view, name='select_exchange_view'),
    path('exchanges/<str:exchange>/', instrument_list_view, name='instrument_list_view'),
    path('exchanges/<str:exchange>/<str:instrument>/', contract_list_view, name='contract_list_view'),
    path('exchanges/<str:exchange>/<str:instrument>/instrument_detail/', instrument_detail, name='instrument_detail'),
    path('exchanges/<str:exchange>/<str:instrument>/roll_calendar/', roll_calendar, name='roll_calendar'),
    path('exchanges/<str:exchange>/<str:instrument>/multiple_price_data', multiple_price_data, name='multiple_price_data'),
    path('exchanges/<str:exchange>/<str:instrument>/adjusted_prices/', adjusted_prices_view, name='adjusted_prices_view'),
    path('exchanges/<str:exchange>/<str:instrument>/<str:contract>/', contract_detail_view, name='contract_detail_view'),

    
    path('data/multiprice/update/', update_multiple_price_data, name='update_multiple_price_data'),

    path('select_instrument/<str:exchange>/', select_instrument_view, name='select_instrument_view'),
    path('fx_price_data/<str:exchange>/<str:instrument>/', fx_price_data_view, name='fx_price_data_view'),

    path('create_instrument/', create_instrument, name='create_instrument'),
    
    path('autotest/', backtest_view, name='backtest_view'),
    path('select-rules/', select_rules_view, name='select_rules'),
    path('select-instruments/', select_instruments_view, name='select_instruments'),

]
