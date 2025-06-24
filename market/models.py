from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

class Offer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="offers")
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='offers/', null=True, blank=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def min_price(self):
        return self.details.aggregate(models.Min('price'))['price__min'] or 0

    @property
    def min_delivery_time(self):
        return self.details.aggregate(models.Min('delivery_time_in_days'))['delivery_time_in_days__min'] or 0

    def __str__(self):
        return self.title


class OfferDetail(models.Model):
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, related_name="details")
    title = models.CharField(max_length=255)
    revisions = models.PositiveIntegerField()
    delivery_time_in_days = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.JSONField(default=list)
    offer_type = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.offer.title} - {self.title}"

class Order(models.Model):
    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    customer_user = models.ForeignKey(User, related_name='customer_orders', on_delete=models.CASCADE)
    business_user = models.ForeignKey(User, related_name='business_orders', on_delete=models.CASCADE)
    offer_detail = models.ForeignKey('OfferDetail', on_delete=models.PROTECT)
    title = models.CharField(max_length=255)
    revisions = models.PositiveIntegerField()
    delivery_time_in_days = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.JSONField(default=list)
    offer_type = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.customer_user} -> {self.business_user})"
    
class Review(models.Model):
    business_user = models.ForeignKey(User, related_name='received_reviews', on_delete=models.CASCADE)
    reviewer = models.ForeignKey(User, related_name='written_reviews', on_delete=models.CASCADE)
    rating = models.IntegerField()
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('business_user', 'reviewer')

    def __str__(self):
        return f"Review by {self.reviewer} for {self.business_user} ({self.rating})"
