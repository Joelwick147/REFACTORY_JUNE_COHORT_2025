from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('brooder_manager', 'Brooder Manager'),
        ('sales_rep', 'Sales Rep'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"

# Farmer model for non-authenticated users (farmers don't login)
class Farmer(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
    ]
    FARMER_CHOICES = [
        ('Starter', 'Starter'),
        ('Returning', 'Returning'),
    ]
    farmer_name = models.CharField(max_length=50)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    farmer_nin = models.CharField(max_length=30, unique=True)
    phone_number = models.CharField(max_length=15)
    recommender_name = models.TextField()
    recommender_nin = models.CharField(max_length=30)
    address = models.TextField(max_length=50)
    email = models.EmailField(max_length=50, unique=True)
    recommender_tel = models.CharField(max_length=15)
    farmer_type = models.CharField(max_length=10, choices=FARMER_CHOICES)
    registration_date = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.farmer_name

# Chick Stock: available chicks for sale
class ChickStock(models.Model):
    CHICK_TYPE_CHOICES = [
        ('Broilers', 'Broilers'),
        ('Layers', 'Layers'),
    ]
    CHICK_BREED_CHOICES = [
        ('local', 'Local'),
        ('exotic', 'Exotic'),
    ]
    batch_number = models.CharField(max_length=50)
    chick_type = models.CharField(max_length=15, choices=CHICK_TYPE_CHOICES)
    chick_breed = models.CharField(max_length=15, choices=CHICK_BREED_CHOICES)
    chick_price = models.PositiveIntegerField(default=1650)
    chick_quantity = models.PositiveIntegerField()
    date_added = models.DateField(auto_now_add=True)
    registered_by = models.CharField(max_length=50)
    chicks_period = models.PositiveIntegerField()
    def __str__(self):
        return self.batch_number

# Chick Request: farmers request chicks, to be approved by manager
class ChickRequest(models.Model):
    CHICK_TYPE_CHOICES = [
        ('Broilers', 'Broilers'),
        ('Layers', 'Layers'),
    ]
    CHICK_BREED_CHOICES = [
        ('local', 'Local'),
        ('exotic', 'Exotic'),
    ]
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('Fulfilled', 'Fulfilled'),
    ]
    YES_NO_CHOICES = [
        ('YES', 'Yes'),
        ('NO', 'No'),
    ]
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('partially paid', 'Partially Paid'),
    ]
    FARMER_TYPES = [
        ('Starter', 'Starter'),
        ('Returning', 'Returning'),
    ]
    farmer = models.ForeignKey(Farmer, on_delete=models.CASCADE)
    farmer_type = models.CharField(max_length=10, choices=FARMER_TYPES)
    chick_type = models.CharField(max_length=15, choices=CHICK_TYPE_CHOICES)
    chick_breed = models.CharField(max_length=15, choices=CHICK_BREED_CHOICES)
    quantity_requested = models.PositiveIntegerField()
    request_date = models.DateTimeField(auto_now_add=True)
    chick_period = models.PositiveIntegerField(default=0)
    took_feeds = models.CharField(max_length=3, choices=YES_NO_CHOICES)
    request_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    delivered = models.CharField(max_length=3, choices=YES_NO_CHOICES, default='NO')
    delivery_date = models.DateField(blank=True, null=True)
    payment_status = models.CharField(max_length=15, choices=PAYMENT_STATUS_CHOICES, default='pending')
    approval_date = models.DateTimeField(null=True, blank=True)
    def __str__(self):
        return f"Request by {self.farmer} for {self.quantity_requested} chicks"

# Sales records of fulfilled chick requests
class Sale(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('partially_paid', 'Partially Paid'),
        ('refunded', 'Refunded'),
        ('cancelled', 'Cancelled'),
    ]
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('credit_card', 'Credit Card'),
        ('mobile_money', 'Mobile Money'),
    ]
    customer = models.ForeignKey(Farmer, on_delete=models.CASCADE, related_name='sales')
    chick_request = models.OneToOneField(ChickRequest, on_delete=models.SET_NULL, null=True, blank=True, related_name='sale')
    sale_date = models.DateTimeField(auto_now_add=True)
    quantity_sold = models.PositiveIntegerField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    feed_bags_eligible = models.PositiveIntegerField(default=2)
    feed_payment_due_date = models.DateField()
    payment_status = models.CharField(max_length=15, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    notes = models.TextField(blank=True)
    def __str__(self):
        return f"Sale to {self.customer.farmer_name} on {self.sale_date.date()}"

# FeedStock model
class FeedStock(models.Model):
    name = models.CharField(max_length=50)
    feed_type = models.CharField(max_length=25)
    feed_brand = models.CharField(max_length=25)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    buying_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    supplier = models.CharField(max_length=255)
    supplier_contact = models.CharField(max_length=15, unique=True)
    date_added = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-date_added']