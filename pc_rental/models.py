from django.db import models
from django.conf import settings
from django.db.models import Avg
from django.utils import timezone

class PC(models.Model):
    name = models.CharField(max_length=100)  
    brand = models.CharField(max_length=50) 
    cpu = models.CharField(max_length=100)  
    ram = models.PositiveIntegerField(help_text="RAM size in GB")  
    storage = models.CharField(max_length=100) 
    gpu = models.CharField(max_length=100, blank=True, null=True)  
    display_size = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True, help_text="Display size in inches")  
    operating_system = models.CharField(max_length=50, blank=True, null=True) 
    description = models.TextField()  
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2, help_text="Rental price per day in USD") 
    is_available = models.BooleanField(blank=True, default=True)
    aviability_date = models.DateField(blank=True, null=True) 
    image = models.ImageField(upload_to="pc_images/")

    def __str__(self):
        return f"{self.name} ({self.cpu}, {self.ram}GB RAM , {self.storage}GB)"


class Rental(models.Model):
    PAYMENT_CHOICES = [('cash', 'Cash'), ('cib', 'CIB'), ('edahabia', 'Edahabia')]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    pc = models.ForeignKey(PC, on_delete=models.CASCADE)
    rental_date = models.DateField()
    return_date = models.DateField()
    total_price = models.DecimalField(max_digits=8, decimal_places=2, blank=True, editable=False)
    is_active = models.BooleanField(default=True)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES)

    # def save(self, *args, **kwargs):
        # days = (self.return_date - self.rental_date).days
        # if days < 1:
        #     days = 1
        # self.total_price = days * self.pc.price_per_day
        # super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user} rented {self.pc}"

# class Review(models.Model):
#     customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     pc = models.ForeignKey(PC, on_delete=models.CASCADE, related_name="reviews")  
#     rating = models.PositiveSmallIntegerField(choices=[(i, str(i)) for i in range(1, 6)])
#     comment = models.TextField(blank=True, null=True) 
#     created_at = models.DateTimeField(auto_now_add=True) 

#     def __str__(self):
#         return f"{self.customer} rated {self.pc} {self.rating}/5"

# class ReviewLikeDislike(models.Model):
#     customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE) 
#     review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name="likes_dislikes")
#     is_like = models.BooleanField()  

#     class Meta:
#         unique_together = ("customer", "review")  

#     def __str__(self):
#         return f"{self.customer} {'liked' if self.is_like else 'disliked'} {self.review}"

