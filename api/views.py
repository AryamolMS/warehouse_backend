from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Supplier,Delivery
from django.contrib.auth.hashers import make_password, check_password
from .models import  Supplier
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime
from .models import Supplier, PickupRequest
from .serializers import PickupRequestSerializer



@api_view(['POST'])
def register_supplier(request):
    try:
        data = request.data

        supplier = Supplier(
            companyName=data.get("companyName"),
            businessType=data.get("businessType"),
            registrationNumber=data.get("registrationNumber"),
            contactPerson=data.get("contactPerson"),
            email=data.get("email"),
            phone=data.get("phone"),
            address=data.get("address"),
            username=data.get("username"),
            password=data.get("password"),  # ⚠️ store plain password
            bankAccount=data.get("bankAccount"),
            ifsc=data.get("ifsc"),
            bankName=data.get("bankName"),
            paymentMethod=data.get("paymentMethod"),
            productCategories=data.get("productCategories"),
        )

        if 'gstFile' in request.FILES:
            gst_file = request.FILES['gstFile']
            supplier.gstFile.put(gst_file, content_type=gst_file.content_type)

        supplier.save()
        return Response({"message": "Supplier registered successfully"}, status=201)

    except Exception as e:
        return Response({"error": str(e)}, status=500)



@api_view(['POST'])
def login_supplier(request):
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response({"error": "Email and password are required"}, status=400)

    try:
        supplier = Supplier.objects.get(email=email)
    except Supplier.DoesNotExist:
        return Response({"error": "Invalid email or password"}, status=401)

    # ⚠️ Direct string comparison since password is not hashed
    if password != supplier.password:
        return Response({"error": "Invalid email or password"}, status=401)

    return Response({
        "message": "Login successful",
        "supplier": {
            "id": str(supplier.id),
            "email": supplier.email,
            "companyName": supplier.companyName,
        }
    }, status=200)



@api_view(['POST'])
def add_delivery(request):
    supplier_id = request.data.get("supplierId")
    item = request.data.get("item")
    quantity = request.data.get("quantity")
    delivery_date = request.data.get("deliveryDate")
    notes = request.data.get("notes")

    # Validate fields
    if not (supplier_id and item and quantity and delivery_date):
        return Response({"error": "All fields except notes are required"}, status=400)

    try:
        supplier = Supplier.objects.get(id=supplier_id)
    except Supplier.DoesNotExist:
        return Response({"error": "Supplier not found"}, status=404)

    # Create delivery linked to the supplier
    delivery = Delivery(
        supplier=supplier,
        item=item,
        quantity=quantity,
        deliveryDate=delivery_date,
        notes=notes or ""
    )
    delivery.save()

    return Response({
        "message": "Delivery added successfully",
        "delivery": {
            "id": str(delivery.id),
            "item": delivery.item,
            "quantity": delivery.quantity,
            "deliveryDate": delivery.deliveryDate,
            "notes": delivery.notes
        }
    }, status=201)

@api_view(['GET'])
def get_deliveries_by_supplier(request, supplier_id):
    try:
        supplier = Supplier.objects.get(id=supplier_id)
    except Supplier.DoesNotExist:
        return Response({"error": "Supplier not found"}, status=404)

    deliveries = Delivery.objects(supplier=supplier)

    data = [
        {
            "id": str(delivery.id),
            "item": delivery.item,
            "quantity": delivery.quantity,
            "deliveryDate": delivery.deliveryDate,
            "notes": delivery.notes,
        }
        for delivery in deliveries
    ]

    return Response(data, status=200)




@api_view(['POST'])
def request_pickup(request):
    data = request.data
    print("Received data:", data)  # 👈 helpful debug line

    required_fields = ['supplierId', 'itemName', 'quantity', 'pickupDate']
    missing = [f for f in required_fields if not data.get(f)]
    if missing:
        return Response({'error': f'Missing required fields: {", ".join(missing)}'}, status=400)

    try:
        supplier = Supplier.objects.get(id=data['supplierId'])
    except Supplier.DoesNotExist:
        return Response({'error': 'Supplier not found'}, status=400)

    try:
        pickup = PickupRequest(
            supplier=supplier,
            item=data['itemName'],
            quantity=int(data['quantity']),
            pickupDate=data['pickupDate'],
            status="Pending",
            createdAt=datetime.utcnow()
        )
        pickup.save()
        return Response({'message': 'Pickup request created successfully!'}, status=201)
    except Exception as e:
        return Response({'error': str(e)}, status=400)


@api_view(['GET'])
def get_pickup_requests(request, supplier_id=None):
    try:
        if supplier_id:
            supplier = Supplier.objects.get(id=supplier_id)
            pickups = PickupRequest.objects(supplier=supplier)
        else:
            pickups = PickupRequest.objects()
        data = [
            {
                "id": str(p.id),
                "supplier": str(p.supplier.id),
                "item": p.item,
                "quantity": p.quantity,
                "pickupDate": p.pickupDate,
                "pickupTime": p.pickupTime,
                "specialInstructions": p.specialInstructions,
                "status": p.status,
                "createdAt": p.createdAt,
            }
            for p in pickups
        ]
        return Response(data, status=200)
    except Exception as e:
        return Response({"error": str(e)}, status=500)


@api_view(['PATCH'])
def update_pickup_status(request, pickup_id):
    try:
        pickup = PickupRequest.objects.get(id=pickup_id)
        new_status = request.data.get("status")
        valid_statuses = [s[0] for s in PickupRequest.STATUS_CHOICES]
        if new_status not in valid_statuses:
            return Response({"error": f"Invalid status. Choose from: {', '.join(valid_statuses)}"}, status=400)
        pickup.status = new_status
        pickup.updatedAt = datetime.utcnow()
        pickup.save()
        return Response({"message": "Status updated successfully"}, status=200)
    except PickupRequest.DoesNotExist:
        return Response({"error": "Pickup request not found"}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=500)

    """
    Delete a pickup request (or cancel it)
    """
    try:
        pickup_request = get_object_or_404(PickupRequest, pk=pk)
        pickup_request.delete()
        
        return Response(
            {'message': 'Pickup request deleted successfully'},
            status=status.HTTP_200_OK
        )
        
    except PickupRequest.DoesNotExist:
        return Response(
            {'error': 'Pickup request not found'},
            status=status.HTTP_404_NOT_FOUND
        )