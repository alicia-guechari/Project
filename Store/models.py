from django.db import models
import datetime
from django.contrib.auth.models import User , AbstractUser, Group, Permission # assuming dj's default user model
from django.db.models.signals import post_save
from django.conf import settings



# Categories of Products

class Category(models.Model):
	id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=255 , unique=True) # unique ensures that no categ can have the same name
	description = models.TextField(blank=True, null=True) # charfield is for short txt like names , txtfield is for long txt like descrp

	def __str__(self):
		return self.name


# address of users

class Address(models.Model):
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customer_groups',  # Add this to prevent clashes
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customer_permissions',  # Add this to prevent clashes
        blank=True
    )
    customer = models.OneToOneField(User, on_delete=models.CASCADE, )
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
	
    def __str__(self):
        return f"{self.street}, {self.city}, {self.country}"
    

# Customers

class Customer(AbstractUser):
    phone = models.CharField(max_length=20, blank=True)
    groups = models.ManyToManyField(Group, related_name="customer_users", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="customer_users_permissions", blank=True)

	    
# Products

class Product(models.Model):
	id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=100 , unique=True)
	price = models.DecimalField(default=0, decimal_places=2, max_digits=6)
	category = models.ForeignKey(Category, on_delete=models.CASCADE, default=1)
	description = models.CharField(max_length=250, default='', blank=True, null=True )
	image = models.ImageField(upload_to='uploads/product/', blank=True, null=True)
	stoke = models.PositiveIntegerField(default=0)

	def __str__(self):
		return self.name # here the name of the product that appears in dj admin pannel


# Customer Orders

class Order(models.Model):
	id = models.AutoField(primary_key=True)
	customer = models.ForeignKey(Customer, on_delete=models.CASCADE , related_name='orders')
	status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ], default='pending')
	total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00) #Stores the total cost of all items in the order
	created_at = models.DateField(default=datetime.datetime.today)
	address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True) # the on_dele... ensures that the order won't be deleted id the addr is deleted

	def __str__(self):
		return f"Order {self.id} - {self.customer.username}"
	# this is for readability in dj admin pannel


class OrderItem(models.Model):
    id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, editable=False) # editable prevents the user from manually editing this val
    
    def save(self, *args, **kwargs):
        self.subtotal = self.quantity * self.price_per_unit
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order {self.order.id}"


# the Cart 

class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return f"Cart of {self.user.username}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
 
    def subtotal(self):
        return self.quantity * self.product.price
    
    def total_price(self):
        return sum(item.subtotal() for item in self.cartitem_set.all())
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name} in {self.cart.Customer.username}'s cart"

