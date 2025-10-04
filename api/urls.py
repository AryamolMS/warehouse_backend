from django.urls import path
from .views import register_supplier, login_supplier

urlpatterns = [
    path('register-supplier/', register_supplier, name='register_supplier'),
    path('login/', login_supplier, name='login_supplier'),
]
