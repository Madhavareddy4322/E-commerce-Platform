from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
class Product(models.Model):
    category    = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name        = models.CharField(max_length=200)
    slug        = models.SlugField(max_length=220, unique=True)
    description = models.TextField(blank=True)
    price       = models.DecimalField(max_digits=10, decimal_places=2)
    stock       = models.PositiveIntegerField()
    image       = models.ImageField(upload_to='products/', blank=True, null=True)
    is_active   = models.BooleanField(default=True)
    created_at  = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

    def average_rating(self):
        agg = self.reviews.aggregate(avg=models.Avg('rating'))
        return agg['avg'] or 0

    def review_count(self):
        return self.reviews.count()

class Coupon(models.Model):
    code         = models.CharField(max_length=20, unique=True)
    description  = models.CharField(max_length=200, blank=True)
    discount_pct = models.PositiveIntegerField(help_text="Percentage discount, e.g. 10 for 10%")
    active       = models.BooleanField(default=True)
    valid_from   = models.DateTimeField()
    valid_to     = models.DateTimeField()

    def __str__(self):
        return f"{self.code} ({self.discount_pct}% off)"

    def is_valid(self):
        now = timezone.now()
        return self.active and self.valid_from <= now <= self.valid_to


class Order(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('SHIPPED', 'Shipped'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    )
    user           = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    created_at     = models.DateTimeField(auto_now_add=True)
    status         = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    total_amount   = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    address        = models.TextField()
    coupon         = models.ForeignKey(Coupon, null=True, blank=True, on_delete=models.SET_NULL)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"

    def final_amount(self):
        return self.total_amount - self.discount_amount


class OrderItem(models.Model):
    order    = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product  = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    price    = models.DecimalField(max_digits=10, decimal_places=2)  # price at purchase

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


class Wishlist(models.Model):
    user     = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist_items')
    product  = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishlisted_by')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user.username} -> {self.product.name}"


class Review(models.Model):
    product   = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user      = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating    = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment   = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('product', 'user')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.product.name} review by {self.user.username}"