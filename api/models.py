# api/models.py
from mongoengine import Document, StringField, EmailField, FileField,IntField, ReferenceField,DateTimeField
from datetime import datetime
import mongoengine


class Supplier(Document):
    # Business Information
    companyName = StringField(required=True, max_length=200)
    businessType = StringField(max_length=100)
    registrationNumber = StringField(max_length=50)
    contactPerson = StringField(max_length=100)
    email = EmailField(required=True, unique=True)
    phone = StringField(max_length=20)
    address = StringField(max_length=500)

    # Account Details
    username = StringField(required=True, unique=True, max_length=50)
    password = StringField(required=True, max_length=128)

    # Payment & Products
    bankAccount = StringField(max_length=50)
    ifsc = StringField(max_length=20)
    bankName = StringField(max_length=100)
    paymentMethod = StringField(max_length=50)
    productCategories = StringField(max_length=200)

    # File Uploads
    gstFile = FileField()

    meta = {
        'collection': 'suppliers',
        'indexes': ['email', 'username']
    }

    def __str__(self):
        return self.companyName

class Delivery(mongoengine.Document):
    supplier = mongoengine.ReferenceField('Supplier', required=True)
    # Item Details
    item = mongoengine.StringField(required=True)
    quantity = mongoengine.IntField(required=True)
    unit = mongoengine.StringField(default='kg')
    category = mongoengine.StringField(default='')
    batchNumber = mongoengine.StringField(default='')
    manufacturer = mongoengine.StringField(default='')
    # Delivery Schedule
    deliveryDate = mongoengine.StringField(required=True)
    deliveryTime = mongoengine.StringField(default='')
    expiryDate = mongoengine.StringField(default='')
    # Storage & Packaging
    storageType = mongoengine.StringField(required=True)
    temperatureRequirement = mongoengine.StringField(default='')
    packagingType = mongoengine.StringField(default='')
    palletCount = mongoengine.IntField(default=0)
    # Safety & Compliance
    hazardousClass = mongoengine.StringField(default='')
    specialHandling = mongoengine.StringField(default='')
    # Documentation
    invoiceNumber = mongoengine.StringField(default='')
    poNumber = mongoengine.StringField(default='')
    # Additional
    notes = mongoengine.StringField(default='')
    # Status & Metadata (ADD THIS)
    status = mongoengine.StringField(
        default='pending',
        choices=['pending', 'accepted', 'rejected']
    )
    createdAt = mongoengine.DateTimeField(default=datetime.now)
    updatedAt = mongoengine.DateTimeField(default=datetime.now)
    
    meta = {
        'collection': 'deliveries',
        'indexes': ['supplier', 'status', '-createdAt']
    }



import mongoengine
from datetime import datetime

class PickupRequest(mongoengine.Document):
    supplier = mongoengine.ReferenceField('Supplier', required=True)  # ← Make sure this line exists
    item = mongoengine.StringField(required=True, max_length=255)
    quantity = mongoengine.IntField(required=True, min_value=0)
    pickupDate = mongoengine.StringField(required=True)
    pickupTime = mongoengine.StringField(max_length=50)
    specialInstructions = mongoengine.StringField(max_length=1000)
    status = mongoengine.StringField(
        required=True,
        default='pending',
        choices=['pending', 'approved', 'rejected', 'completed', 'cancelled']
    )
    rejectionReason = mongoengine.StringField(default='', max_length=500)
    createdAt = mongoengine.DateTimeField(default=datetime.now)
    updatedAt = mongoengine.DateTimeField(default=datetime.now)
    
    meta = {
        'collection': 'pickup_requests',
        'indexes': ['status', 'supplier', '-createdAt']
    }
    
    def save(self, *args, **kwargs):
        self.updatedAt = datetime.now()
        return super(PickupRequest, self).save(*args, **kwargs)


from mongoengine import Document, StringField, IntField, DateTimeField

from datetime import datetime

class WarehouseStock(Document):
    item = StringField(required=True)
    quantity = IntField(required=True, default=0)
    unit = StringField(default="pcs")
    category = StringField(default="")
    storageType = StringField(default="")
    createdAt = DateTimeField(default=datetime.utcnow)
    updatedAt = DateTimeField(default=datetime.utcnow)

    meta = {'collection': 'warehouse_stock'}
