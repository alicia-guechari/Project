from django.db import models
import datetime
from django.contrib.auth.models import User , AbstractUser, Group, Permission # assuming dj's default user model
from django.db.models.signals import post_save
from django.conf import settings



# Categories of Products
class Category(models.Model):
	name = models.CharField(max_length=255 , unique=True) # unique ensures that no categ can have the same name
	description = models.TextField(blank=True, null=True) # charfield is for short txt like names , txtfield is for long txt like descrp

	def __str__(self):
		return self.name


# address of users
class Address(models.Model):
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True, null=True)
    street = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=20)
	
    def __str__(self):
        return f"{self.street}, {self.city}, {self.country}"
    

# Customers
class Customer(AbstractUser):
    phone = models.CharField(max_length=20, blank=True)
    address = models.OneToOneField(Address, on_delete=models.CASCADE, null=True, blank=True)

	    
# Products
class Product(models.Model):
	name = models.CharField(max_length=100, unique=True)
	name = models.CharField(max_length=100 , unique=True)
	price = models.DecimalField(default=0, decimal_places=2, max_digits=6)
	category = models.ForeignKey(Category, on_delete=models.CASCADE)
	description = models.CharField(max_length=250, default='', blank=True, null=True )
	image = models.ImageField(upload_to='media/product/', blank=True, null=True)
	stoke = models.PositiveIntegerField()

	def __str__(self):
		return self.name # here the name of the product that appears in dj admin pannel



# Customer Orders
class Order(models.Model):
    CHOICES =[('pending', 'Pending'),('shipped', 'Shipped'),('delivered', 'Delivered'),('cancelled', 'Cancelled'),]

    user = models.ForeignKey(Customer, on_delete=models.CASCADE , related_name='orders')
    status = models.CharField(max_length=20, choices=CHOICES, default='pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00) #Stores the total cost of all items in the order
    created_at = models.DateField(auto_now=True)
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True) # the on_dele... ensures that the order won't be deleted id the addr is deleted

    def __str__(self):
	    return f"Order {self.id} - {self.customer.username}"
	# this is for readability in dj admin pannel

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, editable=False) # editable prevents the user from manually editing this val
    
    def save(self, *args, **kwargs):
        self.subtotal = self.quantity * self.product.price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order {self.order.id}"



# The Cart 
class Cart(models.Model):
    user = models.OneToOneField(Customer, on_delete=models.CASCADE)

    def __str__(self):
        return f"Cart of {self.user.username}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    
    def save(self, *args, **kwargs):
        self.subtotal = self.quantity * self.product.price
        super().save(*args, **kwargs)
    
    def total_price(self):
        return sum(item.subtotal() for item in self.cartitem_set.all())
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name} in {self.cart.Customer.username}'s cart"

