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
from rest_framework.decorators import api_view
from rest_framework.response import Response
from bson import ObjectId
from bson.errors import InvalidId
from .models import PickupRequest
from .serializers import PickupRequestSerializer, ApproveRejectSerializer
from .models import Delivery, WarehouseStock


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

# Updated API View
@api_view(['POST'])
def add_delivery(request):
    # Required fields
    supplier_id = request.data.get("supplierId")
    item = request.data.get("item")
    quantity = request.data.get("quantity")
    unit = request.data.get("unit", "kg")
    category = request.data.get("category")
    delivery_date = request.data.get("deliveryDate")
    storage_type = request.data.get("storageType")

    # Optional fields
    delivery_time = request.data.get("deliveryTime")
    expiry_date = request.data.get("expiryDate")
    batch_number = request.data.get("batchNumber")
    manufacturer = request.data.get("manufacturer")
    packaging_type = request.data.get("packagingType")
    pallet_count = request.data.get("palletCount")
    temperature_requirement = request.data.get("temperatureRequirement")
    hazardous_class = request.data.get("hazardousClass")
    special_handling = request.data.get("specialHandling")
    invoice_number = request.data.get("invoiceNumber")
    po_number = request.data.get("poNumber")
    notes = request.data.get("notes")

    # Validate required fields
    if not all([supplier_id, item, quantity, unit, category, delivery_date, storage_type]):
        return Response({
            "error": "Missing required fields: supplierId, item, quantity, unit, category, deliveryDate, storageType"
        }, status=400)

    # Validate supplier exists
    try:
        supplier = Supplier.objects.get(id=supplier_id)
    except Supplier.DoesNotExist:
        return Response({"error": "Supplier not found"}, status=404)

    # Validate quantity is positive
    try:
        quantity = int(quantity)
        if quantity <= 0:
            return Response({"error": "Quantity must be a positive number"}, status=400)
    except (ValueError, TypeError):
        return Response({"error": "Invalid quantity value"}, status=400)

    # Validate pallet count if provided
    if pallet_count:
        try:
            pallet_count = int(pallet_count)
            if pallet_count < 0:
                return Response({"error": "Pallet count cannot be negative"}, status=400)
        except (ValueError, TypeError):
            return Response({"error": "Invalid pallet count value"}, status=400)

    # Create delivery with all fields
    from datetime import datetime
    
    delivery = Delivery(
        supplier=supplier,
        # Item Details
        item=item,
        quantity=quantity,
        unit=unit,
        category=category,
        batchNumber=batch_number or "",
        manufacturer=manufacturer or "",
        # Delivery Schedule
        deliveryDate=delivery_date,
        deliveryTime=delivery_time or "",
        expiryDate=expiry_date or "",
        # Storage & Packaging
        storageType=storage_type,
        temperatureRequirement=temperature_requirement or "",
        packagingType=packaging_type or "",
        palletCount=pallet_count,
        # Safety & Compliance
        hazardousClass=hazardous_class or "",
        specialHandling=special_handling or "",
        # Documentation
        invoiceNumber=invoice_number or "",
        poNumber=po_number or "",
        # Additional
        notes=notes or "",
        # Metadata
        createdAt=datetime.utcnow(),
        updatedAt=datetime.utcnow()
    )
    
    delivery.save()

    # Return response with all saved data
    return Response({
        "message": "Stock delivery scheduled successfully",
        "id": str(delivery.id),
        "delivery": {
            "id": str(delivery.id),
            # Item Details
            "item": delivery.item,
            "quantity": delivery.quantity,
            "unit": delivery.unit,
            "category": delivery.category,
            "batchNumber": delivery.batchNumber,
            "manufacturer": delivery.manufacturer,
            # Delivery Schedule
            "deliveryDate": delivery.deliveryDate,
            "deliveryTime": delivery.deliveryTime,
            "expiryDate": delivery.expiryDate,
            # Storage & Packaging
            "storageType": delivery.storageType,
            "temperatureRequirement": delivery.temperatureRequirement,
            "packagingType": delivery.packagingType,
            "palletCount": delivery.palletCount,
            # Safety & Compliance
            "hazardousClass": delivery.hazardousClass,
            "specialHandling": delivery.specialHandling,
            # Documentation
            "invoiceNumber": delivery.invoiceNumber,
            "poNumber": delivery.poNumber,
            # Additional
            "notes": delivery.notes,
            "createdAt": delivery.createdAt.isoformat() if delivery.createdAt else None
        }
    }, status=201)


# Get deliveries for a supplier
@api_view(['GET'])
def get_deliveries(request, supplier_id):
    try:
        supplier = Supplier.objects.get(id=supplier_id)
    except Supplier.DoesNotExist:
        return Response({"error": "Supplier not found"}, status=404)

    deliveries = Delivery.objects(supplier=supplier).order_by('-deliveryDate')
    
    deliveries_data = []
    for delivery in deliveries:
        deliveries_data.append({
            "id": str(delivery.id),
            # Item Details
            "item": delivery.item,
            "quantity": delivery.quantity,
            "unit": delivery.unit,
            "category": delivery.category,
            "batchNumber": delivery.batchNumber,
            "manufacturer": delivery.manufacturer,
            # Delivery Schedule
            "deliveryDate": delivery.deliveryDate,
            "deliveryTime": delivery.deliveryTime,
            "expiryDate": delivery.expiryDate,
            # Storage & Packaging
            "storageType": delivery.storageType,
            "temperatureRequirement": delivery.temperatureRequirement,
            "packagingType": delivery.packagingType,
            "palletCount": delivery.palletCount,
            # Safety & Compliance
            "hazardousClass": delivery.hazardousClass,
            "specialHandling": delivery.specialHandling,
            # Documentation
            "invoiceNumber": delivery.invoiceNumber,
            "poNumber": delivery.poNumber,
            # Additional
            "notes": delivery.notes,
            "createdAt": delivery.createdAt.isoformat() if delivery.createdAt else None
        })

    return Response({"deliveries": deliveries_data}, status=200)


@api_view(['POST'])
def request_pickup(request):
    data = request.data
    print("Received data:", data)  # Debug line

    # Updated required fields to match what frontend sends
    required_fields = ['supplierId', 'item', 'quantity', 'pickupDate']
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
            item=data['item'],
            quantity=int(data['quantity']),
            pickupDate=data['pickupDate'],
            pickupTime=data.get('pickupTime', ''),  # Added default empty string
            specialInstructions=data.get('specialInstructions', ''),  # Added default empty string
            status="pending",  # ✅ Changed from "Pending" to "pending"
            createdAt=datetime.utcnow()
        )
        pickup.save()
        return Response({
            'success': True,
            'message': 'Pickup request created successfully!'
        }, status=201)
    except Exception as e:
        print("Error saving pickup request:", str(e))  # Debug line
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
                "companyName": p.supplier.companyName,  # Add this line
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



@api_view(['GET'])
def get_all_pickup_requests_admin(request):
    """
    Get all pickup requests for admin
    URL: /api/pickup/get_all_pickup/
    """
    try:
        # Get query parameters
        status_filter = request.GET.get('status', None)
        
        # Build query
        queryset = PickupRequest.objects.all()
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Order by creation date (newest first)
        queryset = queryset.order_by('-createdAt')
        
        # Serialize
        data = []
        for p in queryset:
            data.append({
                "id": str(p.id),
                "supplier": str(p.supplier.id),
                "companyName": p.supplier.companyName,
                "item": p.item,
                "quantity": p.quantity,
                "pickupDate": p.pickupDate,
                "pickupTime": p.pickupTime or '',
                "specialInstructions": p.specialInstructions or '',
                "status": p.status,
                "rejectionReason": getattr(p, 'rejectionReason', ''),
                "createdAt": p.createdAt.isoformat() if p.createdAt else None,
                "updatedAt": getattr(p, 'updatedAt', datetime.now()).isoformat(),
            })
        
        return Response({
            'success': True,
            'requests': data,
            'count': len(data)
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PATCH'])
def approve_pickup_request(request, request_id):
    """
    Approve a pickup request
    URL: /api/pickup/approve/<request_id>/
    Method: PATCH
    """
    try:
        # Validate ObjectId
        if not ObjectId.is_valid(request_id):
            return Response({
                'success': False,
                'error': 'Invalid request ID format'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get the pickup request
        try:
            pickup_request = PickupRequest.objects.get(id=request_id)
        except PickupRequest.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Pickup request not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check if already approved
        if pickup_request.status == 'approved':
            return Response({
                'success': False,
                'message': 'Pickup request is already approved'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Update status to approved
        pickup_request.status = 'approved'
        pickup_request.updatedAt = datetime.now()
        pickup_request.save()
        
        # Prepare response data
        response_data = {
            "id": str(pickup_request.id),
            "supplier": str(pickup_request.supplier.id),
            "companyName": pickup_request.supplier.companyName,
            "item": pickup_request.item,
            "quantity": pickup_request.quantity,
            "pickupDate": pickup_request.pickupDate,
            "pickupTime": pickup_request.pickupTime or '',
            "specialInstructions": pickup_request.specialInstructions or '',
            "status": pickup_request.status,
            "rejectionReason": getattr(pickup_request, 'rejectionReason', ''),
            "createdAt": pickup_request.createdAt.isoformat() if pickup_request.createdAt else None,
            "updatedAt": pickup_request.updatedAt.isoformat() if pickup_request.updatedAt else None,
        }
        
        return Response({
            'success': True,
            'message': 'Pickup request approved successfully',
            'data': response_data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PATCH'])
def reject_pickup_request(request, request_id):
    """
    Reject a pickup request
    URL: /api/pickup/reject/<request_id>/
    Method: PATCH
    """
    try:
        # Validate ObjectId
        if not ObjectId.is_valid(request_id):
            return Response({
                'success': False,
                'error': 'Invalid request ID format'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get the pickup request
        try:
            pickup_request = PickupRequest.objects.get(id=request_id)
        except PickupRequest.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Pickup request not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check if already rejected
        if pickup_request.status == 'rejected':
            return Response({
                'success': False,
                'message': 'Pickup request is already rejected'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get optional rejection reason from request body
        reason = request.data.get('reason', '') if request.data else ''
        
        # Update status to rejected
        pickup_request.status = 'rejected'
        if hasattr(pickup_request, 'rejectionReason'):
            pickup_request.rejectionReason = reason
        pickup_request.updatedAt = datetime.now()
        pickup_request.save()
        
        # Prepare response data
        response_data = {
            "id": str(pickup_request.id),
            "supplier": str(pickup_request.supplier.id),
            "companyName": pickup_request.supplier.companyName,
            "item": pickup_request.item,
            "quantity": pickup_request.quantity,
            "pickupDate": pickup_request.pickupDate,
            "pickupTime": pickup_request.pickupTime or '',
            "specialInstructions": pickup_request.specialInstructions or '',
            "status": pickup_request.status,
            "rejectionReason": getattr(pickup_request, 'rejectionReason', reason),
            "createdAt": pickup_request.createdAt.isoformat() if pickup_request.createdAt else None,
            "updatedAt": pickup_request.updatedAt.isoformat() if pickup_request.updatedAt else None,
        }
        
        return Response({
            'success': True,
            'message': 'Pickup request rejected successfully',
            'data': response_data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_all_deliveries(request):
    """
    Get all deliveries from all suppliers for admin
    URL: /api/get_all_deliveries/
    """
    try:
        # Fetch all deliveries from all suppliers
        deliveries = Delivery.objects.all().order_by('-createdAt')
        
        deliveries_data = []
        for delivery in deliveries:
            deliveries_data.append({
                "id": str(delivery.id),
                "supplierName": delivery.supplier.companyName if delivery.supplier else "Unknown",
                "supplierId": str(delivery.supplier.id) if delivery.supplier else None,
                # Item Details
                "item": delivery.item,
                "quantity": delivery.quantity,
                "unit": delivery.unit,
                "category": delivery.category,
                "batchNumber": delivery.batchNumber or '',
                "manufacturer": delivery.manufacturer or '',
                # Delivery Schedule
                "deliveryDate": delivery.deliveryDate,
                "deliveryTime": delivery.deliveryTime or '',
                "expiryDate": delivery.expiryDate or '',
                # Storage & Packaging
                "storageType": delivery.storageType,
                "temperatureRequirement": delivery.temperatureRequirement or '',
                "packagingType": delivery.packagingType or '',
                "palletCount": delivery.palletCount,
                # Safety & Compliance
                "hazardousClass": delivery.hazardousClass or '',
                "specialHandling": delivery.specialHandling or '',
                # Documentation
                "invoiceNumber": delivery.invoiceNumber or '',
                "poNumber": delivery.poNumber or '',
                # Additional
                "notes": delivery.notes or '',
                # Status & Metadata
                "status": getattr(delivery, 'status', 'pending'),
                "createdAt": delivery.createdAt.isoformat() if delivery.createdAt else None,
                "updatedAt": delivery.updatedAt.isoformat() if hasattr(delivery, 'updatedAt') and delivery.updatedAt else None
            })
        
        return Response({
            'success': True,
            'deliveries': deliveries_data,
            'count': len(deliveries_data)
        }, status=200)
        
    except Exception as e:
        print("Error fetching all deliveries:", str(e))
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)



@api_view(['PATCH'])
def accept_delivery(request, delivery_id):
    """
    Accept a delivery and add/update its stock in the warehouse.
    URL: /api/delivery/accept/<delivery_id>/
    Method: PATCH
    """
    try:
        # 1️⃣ Validate delivery ID
        if not ObjectId.is_valid(delivery_id):
            return Response({
                'success': False,
                'error': 'Invalid delivery ID format'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 2️⃣ Retrieve the delivery object
        try:
            delivery = Delivery.objects.get(id=delivery_id)
        except Delivery.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Delivery not found'
            }, status=status.HTTP_404_NOT_FOUND)

        # 3️⃣ Check if already accepted
        if delivery.status == 'accepted':
            return Response({
                'success': False,
                'message': 'Delivery has already been accepted'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 4️⃣ Update delivery status to accepted
        delivery.status = 'accepted'
        delivery.updatedAt = datetime.utcnow()
        delivery.save()

        # 5️⃣ Add or update warehouse stock
        # Check if item already exists in warehouse
        existing_stock = WarehouseStock.objects(item=delivery.item).first()

        if existing_stock:
            # ✅ Update existing stock quantity
            existing_stock.quantity += delivery.quantity
            existing_stock.updatedAt = datetime.utcnow()
            existing_stock.save()
        else:
            # ✅ Create a new stock record
            WarehouseStock.objects.create(
                item=delivery.item,
                quantity=delivery.quantity,
                unit=getattr(delivery, 'unit', 'pcs'),
                category=getattr(delivery, 'category', ''),
                storageType=getattr(delivery, 'storageType', ''),
                createdAt=datetime.utcnow(),
                updatedAt=datetime.utcnow()
            )

        # 6️⃣ Return response
        return Response({
            'success': True,
            'message': 'Delivery accepted and added to warehouse stock',
            'data': {
                'deliveryId': str(delivery.id),
                'item': delivery.item,
                'quantityAdded': delivery.quantity,
                'status': delivery.status,
                'updatedAt': delivery.updatedAt.isoformat()
            }
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PATCH'])
def reject_delivery(request, delivery_id):
    """
    Reject a delivery
    """
    try:
        if not ObjectId.is_valid(delivery_id):
            return Response({
                'success': False,
                'error': 'Invalid delivery ID format'
            }, status=400)
        
        delivery = Delivery.objects.get(id=delivery_id)
        
        delivery.status = 'rejected'
        delivery.updatedAt = datetime.now()
        delivery.save()
        
        return Response({
            'success': True,
            'message': 'Delivery rejected'
        }, status=200)
        
    except Delivery.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Delivery not found'
        }, status=404)
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
def warehouse_inventory(request):
    """
    Get all accepted deliveries (warehouse inventory)
    URL: /api/warehouse_inventory/
    """
    try:
        # Fetch only accepted deliveries
        accepted_deliveries = Delivery.objects.filter(status='accepted').order_by('-createdAt')
        
        inventory_data = []
        for delivery in accepted_deliveries:
            try:
                # Safely get supplier name
                supplier_name = "Unknown Supplier"
                if delivery.supplier:
                    supplier_name = getattr(delivery.supplier, 'companyName', 'Unknown Supplier')
                
                inventory_data.append({
                    "id": str(delivery.id),
                    "supplierName": supplier_name,
                    # Item Details
                    "item": getattr(delivery, 'item', ''),
                    "quantity": getattr(delivery, 'quantity', 0),
                    "unit": getattr(delivery, 'unit', 'kg'),
                    "category": getattr(delivery, 'category', ''),
                    "batchNumber": getattr(delivery, 'batchNumber', ''),
                    "manufacturer": getattr(delivery, 'manufacturer', ''),
                    # Delivery & Expiry
                    "deliveryDate": getattr(delivery, 'deliveryDate', ''),
                    "expiryDate": getattr(delivery, 'expiryDate', ''),
                    # Storage
                    "storageType": getattr(delivery, 'storageType', ''),
                    "temperatureRequirement": getattr(delivery, 'temperatureRequirement', ''),
                    "packagingType": getattr(delivery, 'packagingType', ''),
                    # Additional
                    "notes": getattr(delivery, 'notes', ''),
                    "createdAt": delivery.createdAt.isoformat() if hasattr(delivery, 'createdAt') and delivery.createdAt else None,
                })
            except Exception as item_error:
                print(f"Error processing inventory item {delivery.id}: {str(item_error)}")
                continue
        
        return Response({
            'success': True,
            'inventory': inventory_data,
            'count': len(inventory_data)
        }, status=200)
        
    except Exception as e:
        print("Error fetching warehouse inventory:", str(e))
        import traceback
        traceback.print_exc()
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)

# pickups/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import PickupRequest
from api.models import WarehouseStock

@receiver(post_save, sender=PickupRequest)
def reduce_inventory_on_approval(sender, instance, created, **kwargs):
    # Only reduce inventory when status changes to 'approved'
    if not created and instance.status == 'approved':
        # Get the previous status from database
        if hasattr(instance, '_old_status') and instance._old_status != 'approved':
            # Reduce inventory quantity
            inventory_item = WarehouseStock.objects.get(
                item=instance.item,
                category=instance.category
            )
            
            if inventory_item.quantity >= instance.quantity:
                inventory_item.quantity -= instance.quantity
                inventory_item.save()
            else:
                raise ValueError("Insufficient inventory stock")
