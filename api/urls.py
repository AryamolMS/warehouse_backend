from django.urls import path
from .views import register_supplier, login_supplier,add_delivery,get_deliveries_by_supplier, request_pickup, get_pickup_requests, update_pickup_status

urlpatterns = [
    path('register-supplier/', register_supplier, name='register_supplier'),
    path('login/', login_supplier, name='login_supplier'),

    #Deliveries
    path('add_delivery/', add_delivery, name='add_delivery'),
    path("get_deliveries/<str:supplier_id>/", get_deliveries_by_supplier),

    # ✅ Pickup Requests (MongoEngine-based)
    path('pickup/request/', request_pickup, name='request_pickup'),
    path('pickup/', get_pickup_requests, name='get_all_pickups'),
    path('pickup/<str:supplier_id>/',get_pickup_requests, name='get_pickups_by_supplier'),
    path('pickup/status/<str:pickup_id>/', update_pickup_status, name='update_pickup_status'),
]

