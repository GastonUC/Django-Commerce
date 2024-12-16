from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import AuctionListing, Bid, Comment, Category, Watchlist

class AuctionListingAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "description", "category", "price", "date", "img_url", "user", "state")

class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")

class BidAdmin(admin.ModelAdmin):
    list_display = ("id", "auction", "amount", "user", "bid_date")

class WatchlistAdmin(admin.ModelAdmin):
    list_display = ("id", "auction", "user")

class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "auction", "body", "user", "date")

# Register your models here.
admin.site.register(AuctionListing, AuctionListingAdmin)
admin.site.register(Bid, BidAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(get_user_model())
admin.site.register(Watchlist, WatchlistAdmin)
