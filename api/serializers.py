from rest_framework import serializers
from .models import Supplier,PickupRequest

class SupplierSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    companyName = serializers.CharField(required=True, max_length=200)
    businessType = serializers.CharField(allow_blank=True, required=False)
    registrationNumber = serializers.CharField(allow_blank=True, required=False)
    contactPerson = serializers.CharField(allow_blank=True, required=False)
    email = serializers.EmailField(required=True)
    phone = serializers.CharField(allow_blank=True, required=False)
    address = serializers.CharField(allow_blank=True, required=False)
    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True)
    bankAccount = serializers.CharField(allow_blank=True, required=False)
    ifsc = serializers.CharField(allow_blank=True, required=False)
    bankName = serializers.CharField(allow_blank=True, required=False)
    paymentMethod = serializers.CharField(allow_blank=True, required=False)
    productCategories = serializers.CharField(allow_blank=True, required=False)

    def create(self, validated_data):
        supplier = Supplier(**validated_data)
        supplier.save()
        return supplier


""" Login Serializer """
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class PickupRequestSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    supplier = serializers.CharField()
    item = serializers.CharField(required=True)
    quantity = serializers.IntegerField(required=True)
    pickupDate = serializers.CharField(required=True)
    pickupTime = serializers.CharField(allow_blank=True, required=False)
    specialInstructions = serializers.CharField(allow_blank=True, required=False)
    status = serializers.CharField(read_only=True)
    createdAt = serializers.DateTimeField(read_only=True)
    updatedAt = serializers.DateTimeField(read_only=True)

    def create(self, validated_data):
        pickup_request = PickupRequest(**validated_data)
        pickup_request.save()
        return pickup_request
