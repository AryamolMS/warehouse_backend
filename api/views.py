from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Supplier,Delivery
from django.contrib.auth.hashers import make_password, check_password


@api_view(['POST'])
def register_supplier(request):
    try:
        data = request.data

        # Hash password before saving
        hashed_password = make_password(data.get("password"))

        supplier = Supplier(
            companyName=data.get("companyName"),
            businessType=data.get("businessType"),
            registrationNumber=data.get("registrationNumber"),
            contactPerson=data.get("contactPerson"),
            email=data.get("email"),
            phone=data.get("phone"),
            address=data.get("address"),
            username=data.get("username"),
            password=hashed_password,  # ✅ store hashed password
            bankAccount=data.get("bankAccount"),
            ifsc=data.get("ifsc"),
            bankName=data.get("bankName"),
            paymentMethod=data.get("paymentMethod"),
            productCategories=data.get("productCategories"),
        )

        # Handle GST / License file properly
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

    # ✅ now check against hashed password
    if not check_password(password, supplier.password):
        return Response({"error": "Invalid email or password"}, status=401)

    return Response({
        "message": "Login successful",
        "supplier": {
            "id": str(supplier.id),
            "email": supplier.email,
            "companyName": supplier.companyName,
        }
    })


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
