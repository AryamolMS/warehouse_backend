from django.urls import path
from .views import register_supplier, login_supplier,add_delivery,get_deliveries_by_supplier,add_pickup_request,get_pickups_by_supplier

urlpatterns = [
    path('register-supplier/', register_supplier, name='register_supplier'),
    path('login/', login_supplier, name='login_supplier'),
    path('add_delivery/', add_delivery, name='add_delivery'),
    path("get_deliveries/<str:supplier_id>/", get_deliveries_by_supplier),
    path("add_pickup_request/", add_pickup_request,name="add_pickup_request"),
    path("get_pickups/<str:supplier_id>/", get_pickups_by_supplier,name="get_pickups_by_supplier"),
]
