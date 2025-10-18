from django.urls import path
from .views import register_supplier, login_supplier, request_pickup, get_pickup_requests, add_delivery,get_deliveries,approve_pickup_request,reject_pickup_request, get_all_pickup_requests_admin,accept_delivery,get_all_deliveries,accept_delivery,reject_delivery,warehouse_inventory

urlpatterns = [
    path('register-supplier/', register_supplier, name='register_supplier'),
    path('login/', login_supplier, name='login_supplier'),

    #Deliveries
    path('add_delivery/', add_delivery, name='add_delivery'),
    path('get_deliveries/<str:supplier_id>/',get_deliveries, name='get_deliveries'),
    path('delivery/accept/<str:delivery_id>/', accept_delivery, name='accept_delivery'),

     # Admin Stock Management (NEW)
    path('get_all_deliveries/', get_all_deliveries, name='get_all_deliveries'),
    path('accept_delivery/<str:delivery_id>/', accept_delivery, name='accept_delivery'),
    path('reject_delivery/<str:delivery_id>/', reject_delivery, name='reject_delivery'),
    path('warehouse_inventory/', warehouse_inventory, name='warehouse_inventory'),


    # ✅ Pickup Requests (MongoEngine-based)
    path('pickup/request/', request_pickup, name='request_pickup'),
    path('pickup/get_all_pickup', get_pickup_requests, name='get_pickup_requests'),
    path('pickup/get_all_pickup_requests_admin/', get_all_pickup_requests_admin, name='get_all_pickup_requests_admin'),
    path('pickup/<str:supplier_id>/',get_pickup_requests, name='get_pickups_by_supplier'),
    path('pickup/approve/<str:request_id>/', approve_pickup_request, name='approve-pickup'),
    path('pickup/reject/<str:request_id>/', reject_pickup_request, name='reject-pickup'),
]

