from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Category(models.Model): # Optional for the user
    name = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.name

class AuctionListing(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="users")
    title = models.CharField(max_length=45) #or 50
    description = models.CharField(max_length=250)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, related_name="category")
    price = models.DecimalField(max_digits=9, decimal_places=2)
    # price = models.ForeignKey('Bid', on_delete=models.CASCADE, related_name="price")
    date = models.DateTimeField(auto_now_add=True)
    img_url = models.URLField(blank=True) # Check
    state = models.BooleanField(default=False)

    def __str__(self):
        # return f"{self.id} {self.title} {self.description} {self.price} {self.category} {self.date} {self.img_url}"
        return f"ID: {self.id} Title: {self.title}"

class Bid(models.Model):
    auction = models.ForeignKey(AuctionListing, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=9, decimal_places=2)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bid_date = models.DateTimeField(auto_now_add=True) #because shouldn't change

    def __str__(self):
        return f"{self.amount}"
        # return f"{self.user} bid {self.amount} on {self.auction}"

class Comment(models.Model):
    auction = models.ForeignKey(AuctionListing, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.CharField(max_length=250)
    date = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"Comment: {self.body} on auction {self.auction} created by {self.user}"

class Watchlist(models.Model):
    auction = models.ForeignKey(AuctionListing, on_delete=models.CASCADE) #Add ManyToManyField
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlist_user") #Add ManyToManyField

    class Meta:
        unique_together = ['auction', 'user']

    def __str__(self):
        return f"{self.auction} on user {self.user} watchlist"