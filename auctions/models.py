from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Category(models.Model): # Optional for the user
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name

class AuctionListing(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="users")
    title = models.CharField(max_length=45) #or 50
    description = models.CharField(max_length=250)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="category")
    price = models.DecimalField(max_digits=9, decimal_places=2)
    date = models.DateField(auto_now=True)
    img_url = models.URLField(blank=True) # Check
    state = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.id} {self.title} {self.description} {self.price} {self.category} {self.date} {self.img_url}"

class Bid(models.Model):
    auction = models.ForeignKey(AuctionListing, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=9, decimal_places=2) #or Intege r
    user = models.ForeignKey(User, on_delete=models.CASCADE) # FIX
    bid_date = models.DateField(auto_now=True)

    def __str__(self):
        return self.amount

class Comment(models.Model):
    auction = models.ForeignKey(AuctionListing, on_delete=models.CASCADE)
    body = models.CharField(max_length=250)
    # user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="username") # FIX doesn't need related_name it seems

    def __str__(self):
        return self.body

class Watchlist(models.Model):
    auction = models.ForeignKey(AuctionListing, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlist_user")

    def __str__(self):
        return f"{self.auction} on user {self.user} watchlist"