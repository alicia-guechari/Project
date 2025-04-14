from django.db import models
from django.conf import settings
from django.db.models import Avg
from datetime import datetime

class PC(models.Model):
    name = models.CharField(max_length=100)  
    brand = models.CharField(max_length=50, blank=True, null=True) 
    cpu = models.CharField(max_length=100)  
    ram = models.PositiveIntegerField(help_text="RAM size in GB")  
    storage = models.CharField(max_length=100)  # ex: "512GB SSD + 1TB HDD"
    gpu = models.CharField(max_length=100, blank=True, null=True)  
    display_size = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True, help_text="Display size in inches")  
    operating_system = models.CharField(max_length=50, blank=True, null=True) 
    description = models.TextField(blank=True, null=True)  
    price_per_day = models.DecimalField(max_digits=6, decimal_places=2, help_text="Rental price per day in USD") 
    is_available = models.BooleanField(default=True)  
    image = models.ImageField(upload_to="pc_images/", blank=True, null=True)  

    def __str__(self):
        return f"{self.name} ({self.cpu}, {self.ram}GB RAM , {self.storage}GB)"
    
    def average_rating(self):
        return self.reviews.aggregate(avg_rating=Avg("rating"))["avg_rating"] or 0



class Rental(models.Model):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Who is renting
    pc = models.ForeignKey(PC, on_delete=models.CASCADE)  # Which PC is rented
    rental_date = models.DateTimeField(auto_now_add=True)  # When the rental starts
    return_date = models.DateTimeField(null=True, blank=True)  # When the PC is expected to be returned
    total_price = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)  # Total rental cost
    is_active = models.BooleanField(default=True)  # If the rental is ongoing

    def __str__(self):
        return f"{self.customer} rented {self.pc} on {self.rental_date}"
    
    
    @property  # for calculating the duration of the rental
    def days(self):
        if self.return_date:
            return (self.return_date - self.rental_date).days or 1
        return (datetime.now() - self.rental_date).days or 1

class RentalRequest(models.Model): # to approve the rental request by the admin
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    pc = models.ForeignKey(PC, on_delete=models.CASCADE)
    request_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=10,
        choices=[("pending", "Pending"), ("approved", "Approved"), ("rejected", "Rejected")],
        default="pending",
    )

    def __str__(self):
        return f"{self.customer} requested {self.pc} ({self.status})"


class Review(models.Model):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Who is reviewing
    pc = models.ForeignKey(PC, on_delete=models.CASCADE, related_name="reviews")  # Which PC is reviewed
    rating = models.PositiveSmallIntegerField(choices=[(i, str(i)) for i in range(1, 6)])  # Rating from 1 to 5
    comment = models.TextField(blank=True, null=True)  # Optional review text
    created_at = models.DateTimeField(auto_now_add=True)  # Review date

    def __str__(self):
        return f"{self.customer} rated {self.pc} {self.rating}/5"

class ReviewLikeDislike(models.Model):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Who liked/disliked
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name="likes_dislikes")  # Which review
    is_like = models.BooleanField()  # True = Like, False = Dislike

    class Meta:
        unique_together = ("customer", "review")  # A user can like/dislike a review only once

    def __str__(self):
        return f"{self.customer} {'liked' if self.is_like else 'disliked'} {self.review}"

