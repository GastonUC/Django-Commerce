from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.core.exceptions import ValidationError

from .models import User, Category, AuctionListing, Watchlist, Bid


class CreateListing(forms.Form):
    title = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Title for the Listing'}))
    description = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Description'})) # initial="Title for the Listing"
    # category = forms.Select()
    # bid = forms.DecimalField(max_value=1000000, decimal_places=2, initial=0)
    img_url = forms.URLField(widget=forms.URLInput(attrs={'placeholder': 'https://www.imgur.com'}))

class CreateBid(forms.Form):
    bid = forms.DecimalField(max_value=1000000, decimal_places=2, initial=0, widget=forms.NumberInput(attrs={'placeholder':'Place your bid', 'tabindex':'0'}))

def index(request):
    # auctions = AuctionListing.objects.all()
    return render(request, "auctions/index.html", {
        "Auctions": AuctionListing.objects.all()
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })        

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")



def auction(request, auction_id):
    auction = AuctionListing.objects.get(id=auction_id)
    if request.method == "POST":
        form = CreateBid(request.POST)
        if form.is_valid():
            user_bid = float(form.cleaned_data["bid"])
            actual_bid = auction.price
            if user_bid <= actual_bid:
                messages.error(request, "Sorry, but your bid must be above the present one")
                # raise ValidationError("Sorry, but your bid must be above the present one") # This will only display the validationError mesasge at the top of the page when Developer mode is active
                # return HttpResponseRedirect(reverse("auction", args=(auction_id,)))
            else:
                bid = Bid(
                    auction = auction,
                    amount = user_bid,
                    user = User.objects.get(pk=request.user.id)
                )
                bid.save()

                # Update the auctions's price
                auction.price = bid.amount
                auction.save()
                print("Bid saved")
                # auction.price.save()

    return render(request, "auctions/listing.html", {
        "auction": auction,
        "bid": CreateBid()
    })


@login_required(login_url="login") # Check for redirect_field_name or login_url
def new_listing(request):
    if request.method == "POST":
        form = CreateListing(request.POST)
        bidForm = CreateBid(request.POST)
        if form.is_valid() and bidForm.is_valid():
            title = form.cleaned_data["title"]
            description = form.cleaned_data["description"]
            category = Category.objects.get(pk=int(request.POST["category"]))
            # price = form.cleaned_data["bid"]
            price = bidForm.cleaned_data["bid"]
            img_url = form.cleaned_data["img_url"]
            user = User.objects.get(pk=request.user.id)

            auction = AuctionListing(
                user = user,
                title = title,
                price = price,
                description = description,
                category = category,
                img_url = img_url
            )
            auction.save()

            # bid = Bid(
            #    auction = auction,
            #    amount = price,
            #    user = user
            # )
            # bid.save()

            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/create_listing.html", {
                "form": form
            })
    else:
        return render(request, "auctions/create_listing.html", {
            "form": CreateListing(),
            "bid": CreateBid(),
            "categories": Category.objects.all()
        })


@login_required(login_url="login")
def watchlist(request):
    user_id = User.objects.get(pk=request.user.id)
    # watchlist = Watchlist.objects.filter(user=user_id)

    if request.method == "POST":
        auction_id = request.POST["auction_id"]
        auction = AuctionListing.objects.get(pk=auction_id)
        watchlist = Watchlist(
            auction = auction,
            user = user_id
        )
        watchlist.save()
        
        messages.SUCCESS(request, "Auction added to Watchlist Successfully!")
        # return HttpResponseRedirect(reverse("watchlist"))

    return render(request, "auctions/watchlist.html", {
        "watchlist": watchlist
    })


def categories(request):
    cat = Category.objects.all()
    return render(request, "auctions/categories.html", {
        "categories": cat
    })