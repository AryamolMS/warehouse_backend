from django.urls import path
from .views import register_supplier, login_supplier,add_delivery,get_deliveries_by_supplier

urlpatterns = [
    path('register-supplier/', register_supplier, name='register_supplier'),
    path('login/', login_supplier, name='login_supplier'),
    path('add_delivery/', add_delivery, name='add_delivery'),
    path("get_deliveries/<str:supplier_id>/", get_deliveries_by_supplier),
    
]
