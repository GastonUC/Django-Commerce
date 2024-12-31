from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django import forms

from .models import User, Category, AuctionListing, Watchlist, Bid, Comment


class CreateListing(forms.Form):
    title = forms.CharField(max_length=45, widget=forms.TextInput(attrs={'placeholder': 'Title', 'class': 'form-control'}))
    description = forms.CharField(max_length=250, widget=forms.Textarea(attrs={'placeholder': 'Description', 'class': 'form-control'}))
    img_url = forms.URLField(required=False, widget=forms.URLInput(attrs={'placeholder': 'https://www.imgur.com/myImage','class': 'form-control'}))

class CreateBid(forms.Form):
    bid = forms.DecimalField(max_value=1000000, decimal_places=2, widget=forms.NumberInput(attrs={'placeholder':'Set the price','class': 'form-control', 'tabindex':'0'})) # initial=0, whitout this the form shows the placeholder

class CreateComment(forms.Form):
    body = forms.CharField(label="", max_length=450, widget=forms.Textarea(attrs={'placeholder':'Enter your comment...','class':'form-control'}))

def index(request):
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
    auction = get_object_or_404(AuctionListing, id=auction_id)

    bid_count = Bid.objects.filter(auction=auction_id).count()
    highest_bid = Bid.objects.filter(auction=auction_id).order_by("-amount").first()

    comments = Comment.objects.filter(auction=auction_id)

    end_message = ""
    if auction.state:
        if bid_count < 1:
            end_message = "This auction has ended without any bids"
        else:
            end_message = (f"Congratulations! You have the highest bid of {highest_bid}" if highest_bid.user.id == request.user.id else f"This auction has ended with a winning bid of {highest_bid}") # Trying with ternary operator
        watchlist = False
    else:
        if request.user.is_authenticated:
            watchlist = Watchlist.objects.filter(user=request.user.id, auction=auction).exists()
        else:
            watchlist = False

    if request.method == "POST":
        if request.POST.get("state_auction") == "True":
            auction.state = True
            auction.save()
            messages.success(request, "Auction ended successfully!")
            return HttpResponseRedirect(reverse("auction", args=(auction_id,)))

        # Handle bid form
        form = CreateBid(request.POST)
        if form.is_valid():
            user_bid = float(form.cleaned_data["bid"])
            if user_bid > auction.price:
                bid = Bid(
                    auction = auction,
                    amount = user_bid,
                    user = User.objects.get(pk=request.user.id)
                )
                bid.save()
                # Update the auctions's price
                auction.price = bid.amount
                auction.save()
            else:
                messages.error(request, "Sorry, but your bid must be above the present one")
        else:
            messages.error(request, "Invalid bid form")

    # Render the page after handling POST or for GET requests
    return render(request, "auctions/listing.html", {
        "auction": auction,
        "bid": CreateBid(),
        "watchlist": watchlist,
        "comments": comments,
        "comment_form": CreateComment(),
        "end_message": end_message
    })


@login_required(login_url="login")
def new_listing(request):
    if request.method == "POST":
        form = CreateListing(request.POST)
        bidForm = CreateBid(request.POST)
        if form.is_valid() and bidForm.is_valid():
            title = form.cleaned_data["title"]
            description = form.cleaned_data["description"]
            category_id = request.POST["category"]
            category = Category.objects.get(pk=int(category_id)) if category_id else None
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
    user_id = get_object_or_404(User, pk=request.user.id)

    if request.method == "POST":
        auction_id = request.POST["auction_id"]
        auction = get_object_or_404(AuctionListing, id=auction_id)

        if request.POST.get("state_watchlist") == "True":
            Watchlist.objects.filter(user=user_id, auction=auction).delete()
            message = "Auction removed from Watchlist Successfully!"
        else:
            Watchlist.objects.create(auction=auction, user=user_id)
            message = "Auction added to Watchlist Successfully!"

        messages.success(request, message)
        return HttpResponseRedirect(reverse("auction", args=(auction_id,)))

    watchlist = Watchlist.objects.filter(user=user_id)
    return render(request, "auctions/watchlist.html", {
        "watchlist": watchlist
    })

def categories(request, category=None):
    all_categories = Category.objects.all()
    if category:
        if Category.objects.filter(name=category).exists():
            category_obj = Category.objects.get(name=category)
            auctions = AuctionListing.objects.filter(category=category_obj)
        else:
            messages.error(request, "Category not found.")
            auctions = []
            category_obj = None

        return render(request, "auctions/categories.html", {
            "auctions": auctions,
            "categories": all_categories,
            "selected_category": category_obj
        })
    return render(request, "auctions/categories.html", {
        "categories": all_categories
    })

@login_required(login_url="login")
def comments(request, auction_id):
    auction = get_object_or_404(AuctionListing, id=auction_id)
    
    if request.method == "POST":
        form = CreateComment(request.POST)
        if form.is_valid():
            body = form.cleaned_data["body"]
            user = User.objects.get(pk=request.user.id)

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