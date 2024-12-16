from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.core.exceptions import ValidationError

from .models import User, Category, AuctionListing, Watchlist, Bid, Comment


class CreateListing(forms.Form):
    title = forms.CharField(max_length=45, widget=forms.TextInput(attrs={'placeholder': 'Title, MAX 45 Characters'}))
    description = forms.CharField(max_length=250, widget=forms.Textarea(attrs={'placeholder': 'Description'})) # initial="Title for the Listing"
    # category = forms.Select()
    # bid = forms.DecimalField(max_value=1000000, decimal_places=2, initial=0)
    img_url = forms.URLField(widget=forms.URLInput(attrs={'placeholder': 'https://www.imgur.com'}))

class CreateBid(forms.Form):
    bid = forms.DecimalField(max_value=1000000, decimal_places=2, widget=forms.NumberInput(attrs={'placeholder':'Set the price', 'tabindex':'0'})) # initial=0, whitout this the form shows the placeholder

class CreateComment(forms.Form):
    body = forms.CharField(label="", max_length=450, widget=forms.Textarea(attrs={'placeholder':'Enter your comment...'}))

def index(request):
    # auctions = AuctionListing.objects.all()
    return render(request, "auctions/index.html", {
        "auctions": AuctionListing.objects.all()
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
    try:
        auction = AuctionListing.objects.get(id=auction_id)
    except AuctionListing.DoesNotExist:
        return HttpResponse("Auction not found") # Fix for 404 error page

    bid_count = Bid.objects.filter(auction=auction_id).count()
    highest_bid = Bid.objects.filter(auction=auction_id).order_by("-amount").first()
    # print(bid_count, highest_bid)

    if auction.state:
        if bid_count < 1:
            messages.error(request, "This auction has ended without any bids")
        else:
            messages.success(request, f"This auction has ended with a winning bid of {highest_bid}")
            watchlist = False
    else:
        if request.user.is_authenticated:
            watchlist_item = Watchlist.objects.filter(user=request.user.id, auction=auction)
            watchlist = watchlist_item.exists()
        else:
            watchlist = False

    comments = Comment.objects.filter(auction=auction_id)

    if highest_bid is not None:
        if highest_bid.user == request.user.id:
            messages.success(request, "You have the highest bid on this auction")
        else:
            messages.info(request, f"The highest bid on this auction is from {highest_bid.user}")

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
        "bid": CreateBid(),
        "watchlist": watchlist,
        "comments": comments,
        "comment_form": CreateComment()
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

            messages.success(request, "Auction created successfully!")
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
    try:
        user_id = User.objects.get(pk=request.user.id)
    except User.DoesNotExist:
        messages.error(request, "User not found.")
        return HttpResponseRedirect(reverse("index"))

    if request.method == "POST":
        auction_id = request.POST["auction_id"]
        try:
            auction = AuctionListing.objects.get(pk=auction_id)
        except AuctionListing.DoesNotExist:
            messages.error(request, "Auction not found.")
            return HttpResponseRedirect(reverse("index")) # Check for redirect

        # if Watchlist.objects.filter(user=user_id, auction=auction).exists():
        #     messages.error(request, "Auction already in Watchlist.")
        #     return HttpResponseRedirect(reverse("auction", args=(auction_id,)))
        # else:
        if request.POST.get("state_watchlist") == "True": # Check for this logic, maybe there is a better way
            watchlist_item = Watchlist.objects.filter(
                user=user_id, auction=auction
                )
            watchlist_item.delete()
            messages.success(request, "Auction removed from Watchlist Successfully!")
            return HttpResponseRedirect(reverse("auction", args=(auction_id,)))
        else:
            watchlist_item = Watchlist(
                auction = auction,
                user = user_id
            )
            watchlist_item.save()
            messages.success(request, "Auction added to Watchlist Successfully!")
            return HttpResponseRedirect(reverse("auction", args=(auction_id,)))
    
    watchlist = Watchlist.objects.filter(user=user_id)
    return render(request, "auctions/watchlist.html", {
        "watchlist": watchlist
    })


def categories(request, category=None):
    cat = Category.objects.all()
    if category:
        if Category.objects.filter(name=category).exists():
            category_obj = Category.objects.get(name=category)
            auctions = AuctionListing.objects.filter(category=category_obj)
        else:
            # messages.error(request, "Category not found.")
            # return render(request, "auctions/categories.html", {
            #     "categories": cat
            # }) 
            messages.error(request, "Category not found.")
            auctions = []
            category_obj = None

        return render(request, "auctions/categories.html", {
            "auctions": auctions,
            "categories": cat,
            "selected_category": category_obj
        })
    return render(request, "auctions/categories.html", {
        "categories": cat
    })

@login_required(login_url="login")
def comments(request, auction_id):
    try:
        auction = AuctionListing.objects.get(pk=auction_id)
    except AuctionListing.DoesNotExist:
        messages.error(request, "Auction not found.")
        return HttpResponseRedirect(reverse("index"))
    
    if request.method == "POST":
        form = CreateComment(request.POST)
        print("for now everythibng is working")
        if form.is_valid():
            body = form.cleaned_data["body"]
            user = User.objects.get(pk=request.user.id)
            print(f"This is the body: {body} made from {user}")

            comment = Comment(
                auction = auction,
                user = user,
                body = body
            )
            comment.save()
            messages.success(request, "Comment added successfully!")
        else:
            messages.error(request, "Invalid comment")

    return HttpResponseRedirect(reverse("auction", args=(auction_id,)))