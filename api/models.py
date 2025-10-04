# api/models.py
from mongoengine import Document, StringField, EmailField, FileField

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
