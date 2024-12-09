from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("<int:auction_id>", views.auction, name="auction"),
    path("new", views.new_listing, name="new_listing"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("categories", views.categories, name="categories")
]
