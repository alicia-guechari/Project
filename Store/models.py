from django.db import models
from django.contrib.auth.models import AbstractUser # assuming dj's default user model

# Customers
class Customer(AbstractUser):
    phone = models.CharField(max_length=15)

# address of users
class Address(models.Model):
    user = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='addresses')
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    street = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.street}, {self.city}, {self.country}"

# Categories of Products
class Category(models.Model):
	name = models.CharField(max_length=100 , unique=True) # unique ensures that no categ can have the same name
	description = models.CharField(max_length=250,blank=True, null=True) # charfield is for short txt like names , txtfield is for long txt like descrp

	def __str__(self):
		return self.name

# Products
class Product(models.Model):
	name = models.CharField(max_length=100, unique=True)
	description = models.CharField(max_length=250, blank=True, null=True )
	price = models.DecimalField(decimal_places=2, max_digits=6)
	category = models.ForeignKey(Category, on_delete=models.CASCADE)
	image = models.ImageField(upload_to='media/product/', blank=True, null=True)
	stock = models.PositiveIntegerField()

	def __str__(self):
		return self.name # here the name of the product that appears in dj admin pannel

# Orders
class Order(models.Model):
   # CHOICES =[('pending', 'Pending'),('shipped', 'Shipped'),('delivered', 'Delivered'),('cancelled', 'Cancelled'),]

    user = models.ForeignKey(Customer, on_delete=models.CASCADE , related_name='orders')
    #status = models.CharField(max_length=20, choices=CHOICES, blank=True, default='pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2) #Stores the total cost of all items in the order, this is the total price of the order before taxes and shipping fees are applied
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True) # the on_dele... ensures that the order won't be deleted id the addr is deleted
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
	    return f"Order {self.pk} - {self.user.username}"
	# this is for readability in dj admin pannel

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, editable=False) # editable prevents the user from manually editing this val

    class Meta:
        unique_together = ['order', 'product'] 

    def save(self, *args, **kwargs):
        self.subtotal = self.quantity * self.product.price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order {self.order.pk}"


# Cart 
class Cart(models.Model):
    user = models.OneToOneField(Customer, on_delete=models.CASCADE)

    def total_price(self):
        return sum(item.subtotal for item in self.items.all())
    
    def __str__(self):
        return f"Cart of {self.user.username}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

    class Meta:
        unique_together = ['cart', 'product'] 

    def save(self, *args, **kwargs):
        self.subtotal = self.quantity * self.product.price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in {self.cart.user.username}'s cart"
